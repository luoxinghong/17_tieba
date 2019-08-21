import re,sys
import numpy as np


emoji_pattern = re.compile(
    u"(\ud83d[\ude00-\ude4f])|"  # emoticons
    u"(\ud83d[\u0000-\uddff])|"  # symbols & pictographs (2 of 2)
    u"(\ud83d[\ude80-\udeff])|"  # transport & map symbols
    u"(\uD83E[\uDD00-\uDDFF])|"
    u"(\ud83c[\udf00-\uffff])|"  # symbols & pictographs (1 of 2)
    u"(\ud83c[\udde0-\uddff])|"  # flags (iOS)
    u"([\u2934\u2935]\uFE0F?)|"
    u"([\u3030\u303D]\uFE0F?)|"
    u"([\u3297\u3299]\uFE0F?)|"
    u"([\u203C\u2049]\uFE0F?)|"
    u"([\u00A9\u00AE]\uFE0F?)|"
    u"([\u2122\u2139]\uFE0F?)|"
    u"(\uD83C\uDC04\uFE0F?)|"
    u"(\uD83C\uDCCF\uFE0F?)|"
    u"([\u0023\u002A\u0030-\u0039]\uFE0F?\u20E3)|"
    u"(\u24C2\uFE0F?|[\u2B05-\u2B07\u2B1B\u2B1C\u2B50\u2B55]\uFE0F?)|"
    u"([\u2600-\u26FF]\uFE0F?)|"
    u"([\u2700-\u27BF]\uFE0F?)"
    "+", flags=re.UNICODE)


def remove_emoji(text):
    return emoji_pattern.sub(r'aa', text)


def check_contain_chinese(check_str):
    for ch in check_str:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False

def clean_content(str):
    str = str.replace('\r\n',' ')
    str = str.replace('\r','')
    str = str.replace('\n',' ')
    str = str.lstrip('。').rstrip('0')
    return str.strip()



def isfilter(str):
    if len(str)<=4 or len(str)>=50:
        return True

    ## 过滤有QQ号码、电话号码的
    number = re.findall(r'\d{5}', str)
    if len(number)>0:
        return True

    # 过滤 "顶~~~~~~~~~~" "ddddddd" 之类的
    if len(set([*str]))/len(str)<0.3:
        return True

    if '回复' in str or '.com' in str or 'http' in str or '楼' in str or "贴" in str or "坟" in str:
        return True

    if not check_contain_chinese(str):
        return True

    # 过滤有非法字符的

    # 过滤全英文的

    # 含贴字，楼主

    return False

if __name__ == '__main__':
    string = '1223242421好'
    print(check_contain_chinese(string))

