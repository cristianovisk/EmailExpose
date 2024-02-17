import re
import typer
import threading
import pandas as pd
from lxml import html
from rich import print
import httpx as requests
from rich.live import Live
from functools import cache
from rich.table import Table

app = typer.Typer(help="EmailExpose Check")

def valid_email(email):
    regex = r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$'
    if re.match(regex, email):
        return True
    else:
        return False
    
class Inoitsu:
    def __init__(self) -> None:
        self.emails_leak = {}

    def generate_table(self):
        table = Table(title="E-mails Leaks")
        table.add_column('Detection')
        table.add_column('E-mail')
        table.add_column('Most Recent')
        table.add_column('Total Breaches')
        table.add_column('Sources Breaches')
        table.add_column('Possible Password Leak')

        for email in self.emails_leak.keys():
            table.add_row(
                f'{self.emails_leak[email].get("breach_detect")}', f'{email}', f'{self.emails_leak[email].get("most_recent_breach")}', f'{self.emails_leak[email].get("total_breaches")}', f'{self.__list_to_string(self.emails_leak[email].get("sources_breaches"))}', f'{self.emails_leak[email].get("risk_password_leak")}'
            )
        return table
    
    def __list_to_string(self, list_data):
        if list_data:
            return ', '.join(map(str, list_data))
    
    def generate_output(self):
        print('[green bold][+] [yellow]Output in file "output.xlsx"')
        output_data = []
        for email in self.emails_leak.keys():
            sources = self.__list_to_string(self.emails_leak[email].get("sources_breaches"))
            model = {
                "Detection": f'{self.emails_leak[email].get("breach_detect")}', 
                "E-mail": f'{email}', 
                "Most Recent": f'{self.emails_leak[email].get("most_recent_breach")}', 
                "Total Breaches": f'{self.emails_leak[email].get("total_breaches")}', 
                "Sources Breaches": f'{sources}',
                "Possible Password Leak": f'{self.emails_leak[email].get("risk_password_leak")}'
            }
            output_data.append(model)
        pd.DataFrame(output_data).to_excel('output.xlsx', index=False, sheet_name="REPORT_LEAK_EMAILS_DATA")

    def xpath_parser(self, tree, xpath, item=0, split=False, split_simbol=','):
        if len(tree.xpath(xpath)) == 0:
            return []
        p = tree.xpath(xpath)[item].replace('\xa0', '')
        if split == True and len(p) > 0:
            return p.split(split_simbol)
        if len(p) > 0:
            return p
        else:
            return []
        
    def rm_item_list(self, data_list, item_to_rm):
        if data_list == None:
            return data_list
        for num in range(0, len(data_list)):
            if data_list[num] == item_to_rm:
                data_list.pop(num)
                return data_list

    def filter_list(self, data_list):
        itens_rm = ['Breached Data: ', 'Details:']
        for item in itens_rm:
            data_list = self.rm_item_list(data_list=data_list, item_to_rm=item)
        return data_list

    def check_item_list(self, data_list, item):
        for i in data_list:
            if i == item:
                return True
        return False

    def parser_html_get_info(self, html_data):
        tree = html.fromstring(html_data)
        email = self.xpath_parser(tree=tree, xpath='/html/body/center/div[2]/center/div/blockquote/h3[1]/text()')
        breach = "BREACH NO DETECTED!" if len(self.xpath_parser(tree=tree, xpath='/html/body/center/div[2]/center/div/blockquote/h3[2]/text()')) == 0 else self.xpath_parser(tree=tree, xpath='/html/body/center/div[2]/center/div/blockquote/h3[2]/text()')
        summary = self.xpath_parser(tree=tree, xpath='/html/body/center/div[2]/center/div/blockquote/div[2]/span[2]/text()', split=True)
        sources_breaches = self.filter_list(data_list=list(set(tree.xpath('/html/body/center/div[2]/center/div/blockquote/div[1]/b/text()'))))
        total_breaches = 0 if sources_breaches == None else len(sources_breaches) 
        most_recent_breach = "" if len(self.xpath_parser(tree=tree, xpath='/html/body/center/div[2]/center/div/blockquote/div[2]/b[2]/following-sibling::node()[not(preceding-sibling::img) and not(self::img)]')) == 0 else self.xpath_parser(tree=tree, xpath='/html/body/center/div[2]/center/div/blockquote/div[2]/b[2]/following-sibling::node()[not(preceding-sibling::img) and not(self::img)]')
        risk_password_leak = self.check_item_list(data_list=summary, item='Passwords')
        model = {
            "email": email,
            "breach_detect": breach,
            "risk_password_leak": risk_password_leak,
            "total_breaches": total_breaches,
            "most_recent_breach": most_recent_breach,
            "sources_breaches": sources_breaches,
            "summary": summary
        }
        return model
    
    @cache
    def get_info_email_leak(self, email):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,pt;q=0.8',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundarypQMswTvOTy0JewVy',
            'Origin': 'https://www.hotsheet.com',
            'Pragma': 'no-cache',
            'Referer': 'https://www.hotsheet.com/inoitsu/',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        files = {
            'act': (None, email),
            'accounthide': (None, 'test'),
            'submit': (None, ' go '),
        }
        response = requests.post('https://www.hotsheet.com/inoitsu/', headers=headers, files=files)
        return response.content.decode('utf-8')
    
    @cache
    def consult_email(self, email):
        html_data = self.get_info_email_leak(email=email)
        data_leak = self.parser_html_get_info(html_data=html_data)
        self.emails_leak[email] = data_leak
        return data_leak

    def consult_list_emails(self, emails=list):
        for email in emails:
            if valid_email(email=email):
                self.consult_email(email=email)

@app.command()
def cli(file: str = typer.Option(help="Text file with emails line by line"), output: bool = typer.Option(default=False, help="Flag that output result in file named the 'output.xlsx'"), ):
    with open(file, 'r') as file:
        emails = [line.rstrip() for line in file]
    i = Inoitsu()
    t1 = threading.Thread(target=i.consult_list_emails, args=(emails,))
    t1.run()
    with Live(i.generate_table(), refresh_per_second=2) as live:
        while True:
            live.update(i.generate_table())
            if threading.active_count() == 2:
                if output:
                    i.generate_output()
                break
            
if __name__ == "__main__":
    app()