import subprocess, sys, os, re, png, shutil, zipfile

MAX_COLORS = 256
SCALE = float(sys.argv[2]) if len(sys.argv) > 2 else 50

def convert(file):
    filename = file[:-4]
    print(file[:-4])
    colors = []
    with zipfile.ZipFile('./zip/' + file) as zip:
        with zip.open('obj.mtl') as f_mtl:
            colors = generate_color_array(filename, f_mtl)
        with zip.open('tinker.obj') as f_obj:
            generate_obj(filename, colors, f_obj)

    subprocess.check_call([sys.executable, 'objmc.py', '--objs', filename + '.obj', '--texs', filename + '.png', '--flipuv', '--out', filename + '.json', filename + '.png'])
    shutil.copyfile('ready/' + filename + '.json', 'objmc/assets/minecraft/models/block/' + filename + '.json')
    shutil.copyfile('ready/' + filename + '.png', 'objmc/assets/minecraft/textures/' + filename + '.png')

def generate_color_array(filename, f_mtl):
    lines = f_mtl.readlines()

    def insert_color_row(img, r, g, b):
        row = ()
        for _ in range(MAX_COLORS):
            row = row + (r, g, b)
        img.append(row)
        return img

    colors = ['color_0'] # Insert a black row in case the models does not find the proper color
    img = insert_color_row([], 0, 0, 0)

    for line in lines:
        line = line.decode('utf-8')
        if line[0] == 'n':
            if len(colors) == MAX_COLORS:
                print('Used all ${MAX_COLORS} colors!')
                break # Handle this properly...
            color = line.split()[1]
            colors.append(color)
        elif line[0] == 'K' and line[1] == 'd':
            result = re.search(r"Kd ([\d\.]+) ([\d\.]+) ([\d\.]+)", line)
            r, g, b = int(float(result.group(1)) * 255), int(float(result.group(2)) * 255), int(float(result.group(3)) * 255)
            img = insert_color_row(img, r, g, b)

    for _ in range(MAX_COLORS - len(colors)):
        img = insert_color_row(img, 255, 255, 255)

    with open('tmp/' + filename + '.png', 'wb') as f:
        w = png.Writer(MAX_COLORS, MAX_COLORS, greyscale=False)
        w.write(f, img)
    return colors


def generate_obj(filename, colors, f_obj):
    lines = f_obj.readlines()
    # map (meanx, meany, minz) to (0, 0, 0)
    minx = 9999
    maxx = -9999
    miny = 9999
    maxy = -9999
    minz = 9999
    maxz = -9999
    positions = []
    for line in lines:
        line = line.decode('utf-8')
        if line[0] == 'v':
            result = re.search(r"v\s+([-\d\.]+)\s+([-\d\.]+)\s+([-\d\.]+)", line)
            x, y, z = float(result.group(1)), float(result.group(2)), float(result.group(3))
            if x < minx:
                minx = x
            elif x > maxx:
                maxx = x
            if y < miny:
                miny = y
            elif y > maxy:
                maxy = y
            if z < minz:
                minz = z
            elif z > maxz:
                maxz = z
            positions.append((x, y, z))

    def transform(x, y, z):
        x, y, z = (x - (maxx + minx) / 2), y - (maxy + miny) / 2, z - minz
        x, y, z = x / SCALE, y / SCALE, z / SCALE
        x, y, z = -y, z, -x
        return x, y, z


    color = MAX_COLORS - 1
    with open('tmp/' + filename + '.obj', 'w') as f:
        f.write('o obj_0\n')

        for position in positions:
            x, y, z = transform(position[0], position[1], position[2])
            f.write('v {} {} {}\n'.format(x, y, z))

        for i in range(MAX_COLORS):
            f.write('vt 0.5 {}\n'.format((i + 0.5) / MAX_COLORS))

        for line in lines:
            line = line.decode('utf-8')
            if line[0] == 'u':
                try:
                    color = colors.index(line.split()[1])
                except ValueError:
                    color = 0
            elif line[0] == 'f':
                result = re.search(r"f\s+(\d+)\s+(\d+)\s+(\d+)", line)
                f.write('f {}/{} {}/{} {}/{}\n'.format(result.group(1), color + 1, result.group(2), color + 1, result.group(3), color + 1))

shutil.rmtree('C:/Users/' + os.getlogin() + '/AppData/Roaming/.minecraft/resourcepacks/objmc/assets/minecraft/models/block', ignore_errors=True)
shutil.rmtree('C:/Users/' + os.getlogin() + '/AppData/Roaming/.minecraft/resourcepacks/objmc/assets/minecraft/textures', ignore_errors=True)
shutil.rmtree('objmc/assets/minecraft/models/block', ignore_errors=True)
shutil.rmtree('objmc/assets/minecraft/textures', ignore_errors=True)
os.makedirs('tmp', exist_ok=True)
os.makedirs('ready', exist_ok=True)
os.makedirs('objmc/assets/minecraft/models/block', exist_ok=True)
os.makedirs('objmc/assets/minecraft/textures', exist_ok=True)

if len(sys.argv) > 1:
    convert(sys.argv[1])
else:
    for _, _, files in os.walk("./zip"):
        for file in files:
            if file.endswith('.zip'):
                convert(file)

shutil.copytree('objmc', 'C:/Users/' + os.getlogin() + '/AppData/Roaming/.minecraft/resourcepacks/objmc', dirs_exist_ok=True)
shutil.rmtree('tmp', ignore_errors=True)
shutil.rmtree('ready', ignore_errors=True)