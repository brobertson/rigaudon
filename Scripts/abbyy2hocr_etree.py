from lxml import etree
import HTMLParser
html_parser = HTMLParser.HTMLParser()
DEBUG = False 

def greatest_dimensions(dim_in, test_dim):
    l_out = min(dim_in[0], test_dim[0])
    r_out = max(dim_in[1], test_dim[1])
    t_out = min(dim_in[2], test_dim[2])
    b_out = max(dim_in[3], test_dim[3])
    return [l_out, r_out, t_out, b_out]


def dimensions(char_elem):
    out = [int(char_elem.get('l')), int(char_elem.get('r')), int(char_elem.get('t')), int(char_elem.get('b'))]
    if DEBUG: print out
    return out

def scaled_dimensions(char_elem, page_width, page_height):
	dim = dimensions(char_elem)
	print "dim", dim
	print "page_width", page_width
	print "page_height", page_height
	out = [float(dim[0]) / float(page_width), float(dim[1]) / float(page_width), float(dim[2]) / float(page_height), float(dim[3]) / float(page_height)]
	print out
	return out

def generate_new_output_page():
    root = etree.XML('''<html xmlns:abbyy="http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml">
                       <head>
                         <meta name="ocr-id" value="abbyy"/>
                         <meta name="ocr-recognized" value="lines text"/>
                       </head>
                       <body/>
                      </html>''')
    return root


def output_filepath( base_dir, ident, page_no):
    import os.path
    filename = ident + '_' + str(page_no).zfill(4) + '.html'
    return os.path.join(base_dir,filename)


def hocr_span(class_str):
    return etree.XML('<span class="' + class_str + '"/>')


def add_hocr_dim_to_xml_elem(xml_elem, dim):
    title_str = "bbox {0} {1} {2} {3}".format(dim[0],dim[2],dim[1],dim[3])# ltrb
    xml_elem.set('title',title_str)
    return xml_elem


def main(abbyy_in, dir_out, first_file_num):
    import os.path
    import codecs
    base_name = os.path.split(abbyy_in)[1].split('_')[0]
    print base_name
    word_dimensions = []
    just_started_line = False
    params = method = None
    page_no = first_file_num
    xml_page = current_text_container = xml_para = xml_line = xml_word = None
    for action, elem in etree.iterparse(abbyy_in, events=("start", "end")):
        if DEBUG: print action, elem.tag
        if elem.tag == '{http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml}page':
            if action == 'start':
		page_width = int(elem.get('width'))
		page_height = int(elem.get('height'))
                xml_page = generate_new_output_page()
            elif action == 'end':
                if DEBUG: print 'closing page'
                page_filepath = output_filepath(dir_out, base_name, page_no)
                print "I print to", page_filepath
                outfile = codecs.open(page_filepath,'w','UTF-8')
                outfile.write(etree.tostring(xml_page,encoding=unicode))
                page_no = page_no + 1
        if elem.tag == '{http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml}line':
            if action == 'start':
                if DEBUG: print 'opening line'
                xml_line = hocr_span('ocr_line')
                line_dim = dimensions(elem)
                xml_line = add_hocr_dim_to_xml_elem(xml_line, line_dim)
                just_started_line = True
            elif action == 'end':
                if DEBUG: print 'ending word with dim:', word_dimensions
                xml_word = add_hocr_dim_to_xml_elem(xml_word, word_dimensions)
                xml_line.append(xml_word)
                if DEBUG: print(etree.tostring(xml_word, xml_declaration=False, encoding="UTF-8"))
                if DEBUG: print 'ending line'
                if DEBUG: print (etree.tostring(xml_line, xml_declaration=False, encoding="UTF-8"))
                try:
                    xml_par.append(xml_line)
                except Exception, e:
                    print e
		    #pass
        if elem.tag == '{http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml}charParams' and action == 'start':
            if elem.get('wordStart') == 'true':
                if just_started_line == False:
                    if DEBUG: print 'ending word with dim:', word_dimensions
                    xml_word = add_hocr_dim_to_xml_elem(xml_word, word_dimensions)
                    if DEBUG: print(etree.tostring(xml_word, xml_declaration=False, encoding="UTF-8"))
                    xml_line.append(xml_word)
            if elem.get('wordStart') == 'true' or just_started_line:
                if DEBUG: print 'new word'
                word_dimensions = dimensions(elem)
                xml_word = hocr_span('ocr_word')
            #TODO: fix logic here
            if (not elem.get('wordStart') == 'true'):
                if  elem.text == ' ':
                    if DEBUG: print 'skipping space for dimension'
                else:
                    word_dimensions = greatest_dimensions(word_dimensions, dimensions(elem))
            output = elem.text or ''
                    #try:
            if not xml_word.text:
                xml_word.text = ''
            if not output == ' ':
                    xml_word.text = xml_word.text + output
                    #except:
                    #    xml_word.text = output
            if DEBUG: print output
            just_started_line = False
        if elem.tag == '{http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml}row':
		if action == 'start':
			row_element= etree.XML('<tr/>')
		if action == 'end':
			table_element.append(row_element)
	if elem.tag == '{http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml}cell':
		if action == 'start':
			current_text_container = etree.XML('<td/>')
		if action == 'end':
			row_element.append(current_text_container)
	if elem.tag == '{http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml}block' and elem.get('blockType') == "Table":
		if action == 'start':
			table_element= etree.XML('<table/>')
		if action == 'end':
			xml_body.append(table_element)		
	if elem.tag == '{http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml}block' and elem.get('blockType') == "Text":	
	    if action == 'start':
	        if DEBUG: print 'start carea'
	        current_text_container = hocr_span('ocr_carea')
	    elif action == 'end':
	        if DEBUG: print 'end carea'
	        if DEBUG: print(etree.tostring(current_text_container, xml_declaration=False, encoding="UTF-8"))
	        xml_body = xml_page.xpath('/html/body')[0]
	        xml_body.append(current_text_container)
	        current_text_container = None
	if elem.tag == '{http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml}block' and elem.get('blockType') == "Picture" and action == "start":
		xml_body = xml_page.xpath('/html/body')[0]
	        dim = scaled_dimensions(elem, page_width, page_height)
		xml_body.append(etree.Comment("Picture!: " + str(dim)))
        if elem.tag == '{http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml}par':
            if action == 'start':
                if DEBUG: print 'start paragraph'
                xml_par =  etree.XML('<p/>')
            elif action == 'end':
                if DEBUG: print 'end paragraph'
                try:
                    current_text_container.append(xml_par)
                    xml_par = None
                except Exception, e:
                    print e
		    #pass
                if DEBUG: 
		    if xml_par:
			print(etree.tostring(xml_par, xml_declaration=False, encoding="UTF-8"))
        #elem.clear()
    return params, method


    loads(filename)


if __name__ == "__main__":
    import sys
    #input file, output dir
    import glob, os
    try:
        image_dir = sys.argv[3]
        first_filename =  sorted(glob.glob(image_dir + '/' + '*jp2'))[0]
        first_filename = os.path.split(first_filename)[1]
        print "first_filename", first_filename
        first_file_num_str = first_filename.split('.')[0].split('_')[1]
        print 'first file num:', first_file_num_str
        first_file_num = int(first_file_num_str)
        print 'first file num:', first_file_num
    except:
        first_file_num = 1
    main(sys.argv[1], sys.argv[2], first_file_num)
