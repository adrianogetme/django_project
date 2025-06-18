import os
import polib

def compile_messages():
    po_file = 'locale/lv/LC_MESSAGES/django.po'
    mo_file = 'locale/lv/LC_MESSAGES/django.mo'
    
    if not os.path.exists(po_file):
        print(f"Error: {po_file} not found")
        return
    
    try:
        po = polib.pofile(po_file)
        po.save_as_mofile(mo_file)
        print(f"Successfully compiled {po_file} to {mo_file}")
    except Exception as e:
        print(f"Error compiling messages: {str(e)}")

if __name__ == '__main__':
    compile_messages() 