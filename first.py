import subprocess, sys, os, time, shutil
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

print('Preparing everything, wait...\n')
install('pypng')
install('pillow')
os.makedirs('zip', exist_ok=True)
shutil.copytree('objmc', 'C:/Users/' + os.getlogin() + '/AppData/Roaming/.minecraft/resourcepacks/objmc', dirs_exist_ok=True)
os.remove('first.py')
os.remove('README.md')
os.remove('LICENSE')
shutil.rmtree('docs', ignore_errors=True)
print('\nDone! Closing in 2 seconds...')
time.sleep(2)