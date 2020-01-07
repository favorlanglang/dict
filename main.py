import pandas as pd
import numpy as np
import os
import random
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



def main():
    #------------------ Config ------------------#
    chrome_binary = 'chromium-browser'
    title = "Favorlang Dictionary"
    html_file = "docs/index.html"
    pdfFile = 'docs/favorlang_dict_transcribed.pdf'
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="X-UA-Compatible" content="ie=edge">
        <link href="https://fonts.googleapis.com/css?family=Alegreya&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="style.css">
        <title>{title}</title>
    </head>
        <body>
            <header>
                <ul>
                    <li>{title}</li>
                    <li></li>
                    <li><a href="./favorlang_dict_transcribed.pdf">Download</a></li>
                </ul>
            </header>
            
            <ul class="toc">{toc}</ul>
            
            <div class="dict">
                {dictionary}
            </div>
        </body>
    </html>
    """


    #--------------------- Get data from google sheets -------------------#
    gids = ['679511153', '1931724449', '151044886', '1128079217', '1431072574', '866770763', '1207822401', '396391367', '1345694829', '939992016', '971568665', '1842077571']
    pages = ['妤蓁_13-41', '曉鈞_42-70', '容榕_71-99', '永賦_100-128', '庭瑋_129-157', '飛揚_158-186', '俊宏_187-215', '瑞恩_216-244', '凱弘_247-273', '晴方_274-302', '莊勻_303-331', '峻維_326-360']
    url = "https://docs.google.com/spreadsheets/d/186qohB4p9_ewDqggE547E92bxYTILKuSm26PWljVInk/export?format=csv&gid={gid}"
    dfs = []
    for gid, sheet in zip(gids, pages):
        df = pd.read_csv(url.format(gid=gid), dtype='str').dropna(subset=["詞條", "釋義"]).replace(np.nan, '')
        df['轉寫者'] = sheet
        dfs.append(df)
    merged_df = pd.concat(dfs, sort=False, ignore_index=True)
    merged_df.to_csv("favorlang_dict.csv", index=False)


    #---------------- Convert pd to HTML file ---------------------#
    random.seed(2020)
    toc_id = []
    lemma_id = []
    dict_string = ''
    lemma = "1"
    for idx, row in merged_df.iterrows():
        
        # Check change of alphabet
        if row['詞條'].strip()[0].lower() != lemma[0].lower():
            alphabet = row['詞條'].strip()[0].lower()
            item_id = f"{alphabet}-first"
            if item_id in toc_id or item_id in ["*-first", "_-first"]:
                item_id = None
            else:
                toc_id.append(item_id)
        else:
            item_id = None
        # Write to HTML
        lid = f"{row['詞條'].strip()[0].lower()}" + f"_{str(random.random())[2:7]}"
        item = createItem(row['詞條'].strip(), row['頁數'].strip(), row['中文'].strip(), row['釋義'].strip(), item_id=item_id, lemma_id=lid)
        dict_string += item
        # Record alphabet data for next loop
        lemma = row['詞條'].strip()
    # Write dict toc
    li = ["<li><a href='#" + id_ + f"'>{id_[0].upper()}</a></li>" for id_ in toc_id]
    # Write html template
    html = html_template.format(title=title,
                                dictionary=dict_string,
                                toc=''.join(li))    
    with open(html_file, 'w', encoding="utf-8") as f:
        f.write(html)
    # Print to PDF
    #--------- Print to PDF with Chrome ---------#
    os.system(f'{chrome_binary} --headless --disable-gpu --print-to-pdf={pdfFile} --run-all-compositor-stages-before-draw {html_file}')




if __name__ == "__main__":
    main()
