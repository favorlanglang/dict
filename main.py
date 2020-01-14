import pandas as pd
import numpy as np
import json
import re
import os
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
    ori_def_tag.append(BeautifulSoup(ori_def, "html.parser"))
    if item_id:
        item_tag['id'] = str(item_id)
    if lemma_id:
        lemma_tag['id'] = str(lemma_id)

    return str(item_tag)


def normStr(text):
    text = text.lower().strip()
    new_text = ''
    for c in text:
        replaced = False
        for charset, repl in [("ûúü", "u"), ("óôò", "o"), ("ëêé", "e"), ("âäàá", "a"), ("í", "i"), ("。", "."), ("，", ",")]:
            if c in charset:
                new_text += repl
                replaced = True
                break
        if not replaced:
            new_text += c
    return new_text


def import_from_gsheet():
    gids = ['679511153', '1931724449', '151044886', '1128079217', '1431072574', '866770763', '1207822401', '396391367', '1345694829', '939992016', '971568665', '1842077571']
    pages = ['妤蓁_13-41', '曉鈞_42-70', '容榕_71-99', '永賦_100-128', '庭瑋_129-157', '飛揚_158-186', '俊宏_187-215', '瑞恩_216-244', '凱弘_247-273', '晴方_274-302', '莊勻_303-331', '峻維_326-360']
    url = "https://docs.google.com/spreadsheets/d/186qohB4p9_ewDqggE547E92bxYTILKuSm26PWljVInk/export?format=csv&gid={gid}"
    dfs = []
    for gid, sheet in zip(gids, pages):
        df = pd.read_csv(url.format(gid=gid), dtype='str').dropna(subset=["詞條", "釋義"]).replace(np.nan, '')
        df['轉寫者'] = sheet
        dfs.append(df)
    merged_df = pd.concat(dfs, sort=False, ignore_index=True)
    
    # Strip whitespaces
    for col in merged_df.columns:
        merged_df[col] = pd.core.strings.str_strip(merged_df[col])
    
    # Normalize text
    for col in ['詞條', '釋義']:
        merged_df[col + '_norm'] = [text for text in map(normStr, merged_df[col])]
    
    return merged_df


def get_all_lemma(df, lemma_col='詞條'):
    all_lemma = set(df[lemma_col].values)
    all_lemma2 = list(all_lemma)
    for l in list(all_lemma):
        if '*' in l:
            all_lemma2.remove(l)
    return all_lemma2


def index_lemma_in_def(df, all_lemma, def_col='釋義'):
    indexed_defs = []
    pat = " (" + '|'.join(all_lemma) + ")[\.,;]? "
    for def_ in df[def_col].values:
        # Wrap <a> tag around lemma in definition
        replacement = ' <a class="idx" href="#">\g<1></a> '
        def_ = re.sub(pat, replacement, def_)
        
        # Add href in <a> tag
        tag = BeautifulSoup(def_, "html.parser")
        for a in tag.find_all('a', attrs={'class':'idx'}):
            a["href"] = '#' + a.text.lower() + '_1'
        def_ = str(tag)
        indexed_defs.append(def_)
    return indexed_defs

########------------------------ Main Function --------------------##########

def main():
    #------------------ Config ------------------#
    chrome_binary = 'chromium-browser'
    title = "Favorlang Dictionary"
    html_file = "docs/dict.html"
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
    merged_df = import_from_gsheet()
    output_df = merged_df.copy()
    output_df.columns = ['lemma', 'zh-def', 'syllable', 'ori-def', 'ori-page', 'comment', 'annotator', 'lemma_norm', 'ori-def_norm']
    
    #---------------- Save as text data --------------#
    output_df[['lemma', 'zh-def', 'ori-def', 'ori-page']].to_json("docs/dict.json", orient='records', force_ascii=False)
    output_df[['lemma', 'lemma_norm', 'zh-def', 'ori-def', 'ori-def_norm', 'ori-page']].to_json("docs/dict-normalized.json", orient='records', force_ascii=False)
    output_df[['lemma', 'zh-def', 'ori-def', 'ori-page']].to_csv("docs/dict.csv", index=False)
    merged_df[['詞條', '釋義', '中文', '頁數']].to_json("docs/dict-chinese.json")
    
    #---------------- Index lemma mentioned in def ----------------#
    all_lemma = get_all_lemma(merged_df)
    merged_df['釋義'] = index_lemma_in_def(merged_df, all_lemma)


    #---------------- Convert pd to HTML file ---------------------#
    toc_id = []
    lemma_id = []
    dict_string = ''
    dict_json = []
    lemma = "1"
    lemma_counter = {}
    for idx, row in merged_df.iterrows():
        # Check change of alphabet
        lemma_str = row['詞條'].strip().lower().replace(' ', '')
        if lemma_str[0] != lemma[0].lower():
            alphabet = row['詞條'].strip()[0].lower()
            item_id = f"{alphabet}-first"
            if item_id in toc_id or item_id in ["*-first", "_-first"]:
                item_id = None
            else:
                toc_id.append(item_id)
        else:
            item_id = None
        # Write to HTML
        if lemma_str in lemma_counter.keys():
            lemma_counter[lemma_str] += 1
        else:
            lemma_counter[lemma_str] = 1
        lid = lemma_str + f"_{lemma_counter[lemma_str]}"
        item = createItem(row['詞條'].strip(), row['頁數'].strip(), row['中文'].strip(), row['釋義'].strip(), item_id=item_id, lemma_id=lid)
        dict_string += item
        # Write to json for Vue web page
        dict_json.append({
            'lemma': row['詞條'].strip(),
            'page': row['頁數'].strip(),
            'zh-def': row['中文'].strip(), 
            'ori-def': row['釋義'].strip(),
            'item_id': item_id,
            'lemma_id': lid
        })
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
    # Write JSON
    with open("docs/dict-indexed.json", "w", encoding="utf-8") as f:
        json.dump(dict_json, f, ensure_ascii=False)
    with open("docs/dict-toc.json", "w", encoding="utf-8") as f:
        toc_tup = [(id_, id_[0].upper()) for id_ in toc_id]
        json.dump(toc_tup, f, ensure_ascii=False)
    
    # Print to PDF
    #--------- Print to PDF with Chrome ---------#
    os.system(f'{chrome_binary} --headless --disable-gpu --print-to-pdf={pdfFile} --run-all-compositor-stages-before-draw {html_file}')




if __name__ == "__main__":
    main()
