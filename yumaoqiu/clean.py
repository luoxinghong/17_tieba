import re

import MySQLdb
import pandas as pd

from tieba_tzy.helper import isfilter,clean_content

db_name = 'liyi'
mysql_cn= MySQLdb.connect(host='localhost', port=3306,user='root', passwd='111919', db=db_name,charset='utf8')

## process post df
post_df = pd.read_sql("select * from post;", con=mysql_cn)
post_df[["post_id"]] = post_df[["post_id"]].astype(int)
post_df[["thread_id"]] = post_df[["thread_id"]].astype(int)
post_df = post_df.drop_duplicates()

post_df = post_df.sort_index(by = ["thread_id","post_id"],ascending=[True,True]).reset_index(drop=True)
#
## process comment df
comment_df = pd.read_sql("select * from comment;", con=mysql_cn)
comment_df[["comment_id"]] = comment_df[["comment_id"]].astype(int)
comment_df[["post_id"]] = comment_df[["post_id"]].astype(int)
comment_df = comment_df.drop_duplicates()

comment_df = comment_df.sort_index(by = ["post_id","comment_time","comment_id"],ascending=[True,True,True]).reset_index(drop=True)


## process thread df
thread_df = pd.read_sql("select * from thread;", con=mysql_cn)
thread_df[["thread_id"]] = thread_df[["thread_id"]].astype(int)
thread_df = thread_df.drop_duplicates()

thread_df = thread_df.sort_index(by = ["thread_id"],ascending=True).reset_index(drop=True)


def get_comment_conversation(post_author,post_content,post_id,thread_id):

    comment = {post_author:post_content}
    df = comment_df[comment_df['post_id']==post_id].reset_index(drop=True)

    for row in df.itertuples():
        author,content = getattr(row, 'author').strip(),getattr(row, 'content').strip()

        if content.startswith("回复"):

            try:
                receiver = re.findall(r'(?<=回复).+(?= :)', content)[0].strip().lstrip("@")
                tgt = ''.join(content.split(':')[1:])
                src = comment[receiver]
            except:
                # traceback.print_exc()
                continue

        else:
            tgt = content
            src = post_content
        comment[author] = tgt
        src = clean_content(src)
        tgt = clean_content(tgt)

        if isfilter(src) or isfilter(tgt):
            continue

        writer.write(src+'\t\t'+tgt+'\n')


writer = open(db_name+'.txt','w',encoding='utf-8')
for t in range(len(thread_df)):

    thread_id = thread_df['thread_id'][t]
    thread_author = thread_df['thread_author'][t].strip()
    thread_title = thread_df['thread_title'][t].strip()

    post = post_df[post_df['thread_id'] == thread_id].reset_index(drop=True)

    if len(post)==0 or post.loc[0,'author'].strip() != thread_author:
        continue

    ## 遍历每一层楼的回复
    for p in range(len(post)):
        post_id = post.loc[p,'post_id']
        content = post.loc[p,'content'].strip()


        comment_num = int(post.loc[p,'comment_num'])
        post_author = post.loc[p,'author'].strip()
        if comment_num>0:
            get_comment_conversation(post_author,content,post_id,thread_id)

        if p==0:
            author_content = thread_title + content
            continue

        if content.startswith('回复：'):

            try:
                res_ = re.findall(r'(?<=回复：)\d+(?=楼)', content)
                res = res_[0]
            except:
                continue

            post_source_ = post[post['floor']==res]['content'].values

            # 如果回复的楼层不存在
            if len(post_source_)>0:
                post_source = post_source_[0]
            else:
                continue
            content = content[3+len(res)+2:]
            post.loc[p, 'content'] = content
        else:
            post_source = author_content

        post_source = clean_content(post_source)
        content = clean_content(content)
        if isfilter(post_source) or isfilter(content):
            continue

        writer.write(post_source+'\t\t'+content+'\n')

writer.close()









