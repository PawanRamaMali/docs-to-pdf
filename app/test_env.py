# app/test_env.py
import os
import sys
import traceback

def test_environment():
    results = {
        'python_version': sys.version,
        'python_path': sys.executable,
        'current_dir': os.getcwd(),
        'python_modules': [],
        'win32com_status': 'Not tested',
        'word_status': 'Not tested'
    }
    
    try:
        import pip
        results['installed_packages'] = [str(pkg.key) + '==' + str(pkg.version) for pkg in pip.get_installed_distributions()]
    except:
        results['installed_packages'] = ['Failed to get installed packages']
    
    try:
        import win32com.client
        results['win32com_status'] = 'Imported successfully'
        
        try:
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False
            results['word_status'] = 'Created successfully'
            word.Quit()
        except Exception as e:
            results['word_status'] = f'Failed to create: {str(e)}'
            
    except Exception as e:
        results['win32com_status'] = f'Import failed: {str(e)}'
    
    for key, value in results.items():
        print(f"{key}: {value}")

if __name__ == '__main__':
    test_environment()