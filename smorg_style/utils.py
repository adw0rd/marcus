# coding: utf-8
# import re

# def additional_linebreaks_for_old_articles(text):
#     text = re.sub(r'([\w\d]+[^\>]{1})\n', r'\1<br />', text, re.U)
#     text = re.sub(r'((?:strong|a|b|u|s|i)\>)\n', r'\1<br />', text, re.U)
#
#     br_blocks = []
#     br_blocks.extend(re.findall('\<blockquote[^\>]*\>(.+?)\<\/blockquote\>', text, re.S | re.M | re.U) or [])
#     for br_block in br_blocks:
#         new_block = br_block.replace('\n', '<br />')
#         text = text.replace(br_block, new_block)
#
#     # Remove <br> from <code> and <ul> blocks
#     br_blocks = []
#     br_blocks.extend(re.findall('\<code[^\>]*\>(.+?)\<\/code\>', text, re.S | re.M | re.U) or [])
#     br_blocks.extend(re.findall('\<ul[^\>]*\>(.+?)\<\/ul\>', text, re.S | re.M | re.U) or [])
#     for br_block in br_blocks:
#         new_block = br_block.replace('<br />', '\n').replace('<p>', '').replace('</p>', '\n')
#         text = text.replace(br_block, new_block)
#
#     return text
#
#
# def build_links(text):
#     text = re.sub(
#         '(\s+)(http[s]?\:\/\/[^\s\n\<]+)',
#         r'\1<noindex><a href="\2" rel="nofollow">\2</a></noindex>',
#         text, re.U)
#     return text


def usertext(text, *a, **kw):
    # text = additional_linebreaks_for_old_articles(text)
    # text = build_links(text)
    return text
