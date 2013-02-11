#!/usr/bin/python
# coding: utf-8
import codecs
import os
import sys
head = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
"http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<link rel="stylesheet" type="text/css" href="http://heml.mta.ca/Rigaudon/css/sidebyside.css"/>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<title>"""

section_one = """</title>
</head>
<body>"""

section_one_and_half="""<p><a id="prev" href='"""

section_two="'>Prev</a> <a id='next' href='"
section_three="'>Next</a></p>"
section_four="""<img id="page_image" src='"""
section_five="""' alt="photo"/>
<div id="page_right">
<iframe  frameBorder="0" width="850px" height="1500px"
src='"""
section_six="""'></iframe>
</div>

</body>
</html>"""

IMAGE_WEB_DESTINATION_PREFIX = 'http://heml.mta.ca/Rigaudon/Images/Color/'
TEXT_WEB_DESTINATION_PREFIX = 'http://heml.mta.ca/Rigaudon/'
print "reading dir ", sys.argv[1]
dir_in = sys.argv[1]
dir_out = sys.argv[2]
if  not os.path.isdir(dir_in) or not os.path.isdir(dir_out):
        print "usage: spellcheck.csv dir_in dir_out"
        exit()
pages = os.listdir(dir_in)
#we skip pages that aren't hocr
pages_filtered = [page for page in pages if '.html' in page]
pages_filtered.sort()
#count = len(pages_filtered)
for i, page in enumerate(pages_filtered):
    fileIn_name = os.path.join(dir_in,page)
    print fileIn_name
    [text_name,page_number] = page.split('_')
    [real_number,file_extension] = page_number.split('.')
    if i == 0:
        prev_page = ''
    else:
        prev_page = pages_filtered[i - 1]
        
    if i == len(pages_filtered) -1:
        next_page = ''
    else:
        next_page = pages_filtered[i + 1]
    fileOut_name = os.path.join(dir_out,page)
    fileOut = codecs.open(fileOut_name, 'w','utf-8')
    archive_source = 'http://www.archive.org/details/' + text_name
    image_url = IMAGE_WEB_DESTINATION_PREFIX + text_name + '_color' + '/' + text_name + '_' + real_number + '.jpg'
    text_url = TEXT_WEB_DESTINATION_PREFIX + text_name + '_jp2' + '/' + dir_in  + page
    h1_element = '<h1><a href="' + archive_source + '">' + text_name + "</a> Page " + real_number + "</h1>"
    out_string = head + text_name + " Page " + real_number + section_one + h1_element + section_one_and_half + prev_page + section_two + next_page + section_three
    out_string += section_four + image_url + section_five + text_url + section_six
    fileOut.write(out_string)
    fileOut.close()
    

    
            
                       
