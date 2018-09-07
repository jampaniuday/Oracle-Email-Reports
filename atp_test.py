import requests
from lxml import html
import re
import time
import datetime
import cx_Oracle
import sys
import os.path
sys.path.append(os.path.join(os.path.dirname( __file__ ),'functions'))
from my_email import Email
from my_settings import ora_con_str
requests.packages.urllib3.disable_warnings()
global reportName
reportName = "ATP Check"

def main(reportName):
    top_sellers = get_top_sellers()
    #fp_top_sellers = get_top_sellers("FL")

    # get a session ID
    page = requests.get("https://www.bimba.com/Support/Commercial-Support/Price-And-Delivery/")

    # find ssid with regex
    find_ssid_search = "(?<=ssid\=).+?(?=\")"
    pattern = re.compile(find_ssid_search)
    found_ssid = re.findall(pattern, page.text)

    # create email message contents
    array = "No ATP Errors Today"

    # loop through top sellers and check atp for a qty of 2
    for a,i in enumerate(top_sellers):
        atp_request = requests.post("https://bimbanet.com/mrcjava/servlet/BIMBANET.M00700s", data = {
        'CALCULA001' : {i[0],  ''},
        'CALCULA002' : {'2',''},      
        'btn_accept' : 'Request+Part',
        'action_mode' : 'AUR',
        'work_with' : '0',
        'debug' : '0',
        'slnk' : '0',
        'one_step' : '99',
        'act_rule' : '0',
        'recpos' : '0',
        'add_redir' : '',
        'upd_redir' : '',
        'dlt_redir' : '',
        'all_redir' : 'BIMBANET.I00700s?slnk=1&ssid='+ found_ssid[0] + '&CALCULA001='+i[0]+'&CALCULA002=2',
        'add_message' : '',
        'update_message' : '',
        'delete_message' : '',
        'all_message' : '',
        'pageName' : '',
        'ajax_form' : '0',
        'preview' : '0',
        'max_rows' : '1',
        'isReadE' : '1',
        'ssid' : found_ssid[0]
        }, verify=False)

        # get HTML result
        tree = html.fromstring(atp_request.content)

        # find the date section
        date = tree.xpath('//td[@class="two"]/text()')

        # if a date is given there should be success here
        try:
            if str(date[3].strip()) == "Contact Bimba": work_days = 23
               
            else: 
                work_days = int(get_work_days(datetime.datetime.strptime(date[3].strip(), "%m/%d/%y").date()))
                
        # these are dates that say "TBD"
        except:
            work_days = 13
            pass

        # if work days was calculated
        if isinstance( work_days, int ):

            # if the ATP was not a good number
            if (i[3] =='OL' and work_days > 9) or (i[3] == 'FL' and work_days > 10):

                # if this is the first recored, then create the array header and make a nice table 
                if array == "No ATP Errors Today": array =  """<style type="text/css">
.tg  {border-collapse:collapse;border-spacing:0;border-color:#aaa;border-width:1px;border-style:solid;margin:0px auto;}
.tg td{font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:0px;overflow:hidden;word-break:normal;border-color:#aaa;color:#333;background-color:#fff;}
.tg th{font-family:Arial, sans-serif;font-size:14px;font-weight:normal;padding:10px 5px;border-style:solid;border-width:0px;overflow:hidden;word-break:normal;border-color:#aaa;color:#fff;background-color:#f38630;}
.tg .tg-baqh{text-align:center;vertical-align:top}
.tg .tg-j2zy{background-color:#FCFBE3;vertical-align:top}
.tg .tg-yw4l{vertical-align:top}
th.tg-sort-header::-moz-selection { background:transparent; }th.tg-sort-header::selection      { background:transparent; }th.tg-sort-header { cursor:pointer; }table th.tg-sort-header:after {  content:'';  float:right;  margin-top:7px;  border-width:0 4px 4px;  border-style:solid;  border-color:#404040 transparent;  visibility:hidden;  }table th.tg-sort-header:hover:after {  visibility:visible;  }table th.tg-sort-desc:after,table th.tg-sort-asc:after,table th.tg-sort-asc:hover:after {  visibility:visible;  opacity:0.4;  }table th.tg-sort-desc:after {  border-bottom:none;  border-width:4px 4px 0;  }@media screen and (max-width: 767px) {.tg {width: auto !important;}.tg col {width: auto !important;}.tg-wrap {overflow-x: auto;-webkit-overflow-scrolling: touch;margin: auto 0px;}}</style>
<div class="tg-wrap"><table id="tg-HdWXw" class="tg"><tr>
            <th class="tg-baqh">Item</th>
            <th class="tg-baqh">Lead Time<br></th>
          </tr>"""
                
                # add heading to array
                array += """<tr>
            <td class="tg-j2zy">"""+str(i[0])+"""</td>
            <td class="tg-j2zy">"""+ str(work_days) + """</td>
          </tr>
          """
               
        # add TBD items to array      
        else: 
            if array == "No ATP Errors Today": array =  """<style type="text/css">
.tg  {border-collapse:collapse;border-spacing:0;border-color:#aaa;border-width:1px;border-style:solid;margin:0px auto;}
.tg td{font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:0px;overflow:hidden;word-break:normal;border-color:#aaa;color:#333;background-color:#fff;}
.tg th{font-family:Arial, sans-serif;font-size:14px;font-weight:normal;padding:10px 5px;border-style:solid;border-width:0px;overflow:hidden;word-break:normal;border-color:#aaa;color:#fff;background-color:#f38630;}
.tg .tg-baqh{text-align:center;vertical-align:top}
.tg .tg-j2zy{background-color:#FCFBE3;vertical-align:top}
.tg .tg-yw4l{vertical-align:top}
th.tg-sort-header::-moz-selection { background:transparent; }th.tg-sort-header::selection      { background:transparent; }th.tg-sort-header { cursor:pointer; }table th.tg-sort-header:after {  content:'';  float:right;  margin-top:7px;  border-width:0 4px 4px;  border-style:solid;  border-color:#404040 transparent;  visibility:hidden;  }table th.tg-sort-header:hover:after {  visibility:visible;  }table th.tg-sort-desc:after,table th.tg-sort-asc:after,table th.tg-sort-asc:hover:after {  visibility:visible;  opacity:0.4;  }table th.tg-sort-desc:after {  border-bottom:none;  border-width:4px 4px 0;  }@media screen and (max-width: 767px) {.tg {width: auto !important;}.tg col {width: auto !important;}.tg-wrap {overflow-x: auto;-webkit-overflow-scrolling: touch;margin: auto 0px;}}</style>
<div class="tg-wrap"><table id="tg-HdWXw" class="tg"><tr>
            <th class="tg-baqh">Item</th>
            <th class="tg-baqh">Lead Time<br></th>
          </tr>"""
            array += """<tr>
        <td class="tg-j2zy">"""+str(i[0])+"""</td>
        <td class="tg-j2zy">"""+ str(work_days) + """</td>
      </tr>
      """

    # close HTML table
    array += """</table></div>
<script type="text/javascript" charset="utf-8">var TgTableSort=window.TgTableSort||function(n,t){"use strict";function r(n,t){for(var e=[],o=n.childNodes,i=0;i<o.length;++i){var u=o[i];if("."==t.substring(0,1)){var a=t.substring(1);f(u,a)&&e.push(u)}else u.nodeName.toLowerCase()==t&&e.push(u);var c=r(u,t);e=e.concat(c)}return e}function e(n,t){var e=[],o=r(n,"tr");return o.forEach(function(n){var o=r(n,"td");t>=0&&t<o.length&&e.push(o[t])}),e}function o(n){return n.textContent||n.innerText||""}function i(n){return n.innerHTML||""}function u(n,t){var r=e(n,t);return r.map(o)}function a(n,t){var r=e(n,t);return r.map(i)}function c(n){var t=n.className||"";return t.match(/\S+/g)||[]}function f(n,t){return-1!=c(n).indexOf(t)}function s(n,t){f(n,t)||(n.className+=" "+t)}function d(n,t){if(f(n,t)){var r=c(n),e=r.indexOf(t);r.splice(e,1),n.className=r.join(" ")}}function v(n){d(n,L),d(n,E)}function l(n,t,e){r(n,"."+E).map(v),r(n,"."+L).map(v),e==T?s(t,E):s(t,L)}function g(n){return function(t,r){var e=n*t.str.localeCompare(r.str);return 0==e&&(e=t.index-r.index),e}}function h(n){return function(t,r){var e=+t.str,o=+r.str;return e==o?t.index-r.index:n*(e-o)}}function m(n,t,r){var e=u(n,t),o=e.map(function(n,t){return{str:n,index:t}}),i=e&&-1==e.map(isNaN).indexOf(!0),a=i?h(r):g(r);return o.sort(a),o.map(function(n){return n.index})}function p(n,t,r,o){for(var i=f(o,E)?N:T,u=m(n,r,i),c=0;t>c;++c){var s=e(n,c),d=a(n,c);s.forEach(function(n,t){n.innerHTML=d[u[t]]})}l(n,o,i)}function x(n,t){var r=t.length;t.forEach(function(t,e){t.addEventListener("click",function(){p(n,r,e,t)}),s(t,"tg-sort-header")})}var T=1,N=-1,E="tg-sort-asc",L="tg-sort-desc";return function(t){var e=n.getElementById(t),o=r(e,"tr"),i=o.length>0?r(o[0],"td"):[];0==i.length&&(i=r(o[0],"th"));for(var u=1;u<o.length;++u){var a=r(o[u],"td");if(a.length!=i.length)return}x(e,i)}}(document);document.addEventListener("DOMContentLoaded",function(n){TgTableSort("tg-HdWXw")});</script>"""
    
    htmlTable = """<center><p>ATP Check Failures</p><br>""" + array + """</center>""" 
    
    # send the email    
    Email(reportName, htmlTable).SendMail()

def get_work_days(atp_date):
    sql = "select apps.xxbim_get_working_days(85, sysdate, to_date('" + str(atp_date) + "' ,'YYYY-MM-DD')) from dual"
    con = cx_Oracle.connect(ora_con_str['UserName'],ora_con_str['Password'],ora_con_str['TNS'])
    cur = con.cursor()
    cur.execute(sql)
    a = cur.fetchone()
    cur.close()
    return a[0]

def get_top_sellers():

    # get 50 top sellers, non shelving, from FP and OL
    sql = """select distinct * from (select case when msi.segment1 like '%*%' then msi.description else msi.segment1 end item, FULL_LEAD_TIME, msi.attribute7, msi.planner_code
from mtl_system_items_b msi
, MTL_ITEM_CATEGORIES_V cat
where msi.organization_id = 85
and inventory_item_status_code = 'Active'
and planner_Code in ('OL', 'FL')
and to_number(msi.attribute7) > 1
and msi.organization_id = cat.organization_id(+)
    and inventory_item_status_code = 'Active'
    and cat.structure_id(+) = '50415'
    and msi.segment1 not like '%00BI'
    and msi.inventory_item_id = cat.inventory_item_id(+)
    and cat.category_concat_segs = 'Standard'
    order by to_number(attribute7) desc

    ) where rownum < 600
    order by 4,1
"""
    con = cx_Oracle.connect(ora_con_str['UserName'],ora_con_str['Password'],ora_con_str['TNS'])
    cur = con.cursor()
    cur.execute(sql)
    results = cur.fetchall()
    cur.close()
    return results

try:
    main(reportName)
except BaseException as e:
    print(str(e))
    Email(reportName + ' error', "<br><center>" + str(e) + "</center>").SendMail()

    pass
