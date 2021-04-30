import subprocess

def build_objects(sources):
    for src in sources:
        subprocess.check_call([
            "gnatmake",
            "-g",
            src,
            "-c"
        ])

def make_shared(objects):
    subprocess.check_call([
        "gcc",
        "-shared",
        "-o",
        "bin/lib/libtest_ada.so"
    ] + objects)

    for obj in objects:
        subprocess.check_call([
            "rm",
            "-f",
            obj
        ])

        subprocess.check_call([
            "rm",
            "-f",
            obj.replace(".o", ".ali")
        ])

def run():
    sources = [
        'src/ada/test_a/test_a.ads'
    ]

    objects = []
    for src in sources:
        objects.append(src.split('/')[-1].replace(".ads", ".o"))

    build_objects(sources)
    make_shared(objects)


if __name__ == '__main__':
    run()