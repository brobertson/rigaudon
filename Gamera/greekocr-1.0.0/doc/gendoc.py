#!/usr/bin/env python

from gamera import gendoc

if __name__ == '__main__':
   # Step 1:
   # Import all of the plugins to document.
   # Be careful not to load the core plugins, or they
   # will be documented here, too.
   # If the plugins are not already installed, we'll just ignore
   # them and generate the narrative documentation.
   try:
      from gamera.toolkits.greekocr.plugins import clear
   except ImportError:
      print "WARNING:"
      print "This `greekocr` toolkit must be installed before generating"
      print "the documentation.  For now, the system will skip generating"
      print "documentation for the plugins."
      print

   # Step 2:
   # Generate documentation for this toolkit
   # This will handle any commandline arguments if necessary
   gendoc.gendoc(classes=[("gamera.toolkits.greekocr.greekocr",
                           "GreekOCR",
                           "__init__" +\
                           " load_trainingdata" +\
                           " get_page_glyphs" +\
                           " process_image" +\
                           " save_debug_images" +\
                           " save_text_unicode" +\
                           " save_text_teubner")],
                 plugins=[],
                 sourceforge_logo=False)
