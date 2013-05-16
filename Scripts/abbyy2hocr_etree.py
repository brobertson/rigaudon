from lxml import etree
#from cStringIO import StringIO

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


def generate_new_output_page(page_no):
    root = etree.XML('''<html xmlns:abbyy="http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml">
                       <head>
                         <meta name="ocr-id" value="abbyy"/>
                         <meta name="ocr-recognized" value="lines text"/>
                       </head>
                       <body/>
                      </html>''')
    print 'new page:',page_no
    return root

def hocr_span(class_str):
    return etree.XML('<span class="' + class_str + '"/>')

def add_hocr_dim_to_xml_elem(xml_elem, dim):
    title_str = "bbox {0} {1} {2} {3}".format(dim[0],dim[2],dim[1],dim[3])# ltrb
    xml_elem.set('title',title_str)
    return xml_elem

def loads(data):
    word_dimensions = []
    just_started_line = False
    params = method = None
    page_no = 0
    xml_page = xml_carea = xml_para = xml_line = xml_word = None
    for action, elem in etree.iterparse(data, events=("start", "end")):
        if DEBUG: print action, elem.tag
        if elem.tag == '{http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml}page':
            if action == 'start':
                xml_page = generate_new_output_page(page_no)
            elif action == 'end':
                if DEBUG: print 'closing page'
                page_no = page_no + 1
                print(etree.tostring(xml_page, xml_declaration=False, pretty_print=True, encoding="UTF-8"))
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
                except:
                    pass
        if elem.tag == '{http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml}charParams' and action == 'start':
            if elem.get('wordStart') == 'true':
                if just_started_line == False:
                    if DEBUG: print 'ending word with dim:', word_dimensions
                    xml_word = add_hocr_dim_to_xml_elem(xml_word, word_dimensions)
                    if DEBUG: print(etree.tostring(xml_word, xml_declaration=False, encoding="UTF-8"))
                    xml_line.append(xml_word)
                if DEBUG: print 'new word'
                word_dimensions = dimensions(elem)
                xml_word = hocr_span('ocr_word')
            #TODO: fix logic here
            else:
                if  elem.text == ' ':
                    if DEBUG: print 'skipping space for dimension'
                else:
                    word_dimensions = greatest_dimensions(word_dimensions, dimensions(elem))
            output = elem.text or ''
            try:
                xml_word.text = xml_word.text + output
            except:
                xml_word.text = output
            if DEBUG: print output
            just_started_line = False
        if elem.tag == '{http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml}block':
            if action == 'start':
                if DEBUG: print 'start carea'
                xml_carea = hocr_span('ocr_carea')
            elif action == 'end':
                if DEBUG: print 'end carea'
                if DEBUG: print(etree.tostring(xml_carea, xml_declaration=False, encoding="UTF-8"))
                xml_body = xml_page.xpath('/html/body')[0]
                xml_body.append(xml_carea)
        if elem.tag == '{http://www.abbyy.com/FineReader_xml/FineReader6-schema-v1.xml}par':
            if action == 'start':
                if DEBUG: print 'start paragraph'
                xml_par =  etree.XML('<p/>')
            elif action == 'end':
                if DEBUG: print 'end paragraph'
                try:
                    xml_carea.append(xml_par)
                except:
                    pass
                if DEBUG: print(etree.tostring(xml_par, xml_declaration=False, encoding="UTF-8"))
        #elem.clear()
    return params, method

def main(filename, output_dir):

    loads(filename)

if __name__ == "__main__":
    import sys
    #input file, output dir
    main(sys.argv[1], sys.argv[2])
