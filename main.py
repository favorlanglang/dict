import pandas as pd
from bs4 import BeautifulSoup

def createItem(lemma: str, page: str, zh_def: str, ori_def: str, item_id=None, lemma_id=None):
    soup = BeautifulSoup(features="html.parser")

    # Create tags
    item_tag = soup.new_tag("div", attrs={'class': 'item'})
    lemma_tag = soup.new_tag("div", attrs={'class': 'lemma'})
    page_tag = soup.new_tag("span", attrs={'class': 'page'})
    zh_def_tag = soup.new_tag("p", attrs={'class': 'zh-def'})
    ori_def_tag = soup.new_tag("p", attrs={'class': 'ori-def'})
    # Structure html
    item_tag.append(lemma_tag)
    item_tag.append(page_tag)
    item_tag.append(zh_def_tag)
    item_tag.append(ori_def_tag)

    # Write data
    lemma_tag.string = lemma
    page_tag.string = page
    zh_def_tag.string = zh_def
    ori_def_tag.string = ori_def
    if item_id:
        item_tag['id'] = str(item_id)
    if lemma_id:
        lemma_tag['id'] = str(lemma_id)

    return str(item_tag)


#------------- Sheet url ---------------#
# https://docs.google.com/spreadsheets/d/186qohB4p9_ewDqggE547E92bxYTILKuSm26PWljVInk/edit#gid=151044886
# 
# 