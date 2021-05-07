import subprocess
import os

def build_objects(sources, compiler, compiler_options, linker_options):
    for src in sources:
        try:
            subprocess.check_call([
                compiler,
                "-g",
                "-fPIC"
                src,
                "-c",
            ] + compiler_options)
        except subprocess.CalledProcessError:
            return False

    return True

def make_shared(objects, compiler):

    os.makedirs(os.path.join("bin", "lib"), exist_ok=True)

    success = True

    if compiler == 'gnatmake':
        compiler = 'gcc'

    try:
        subprocess.check_call([
            compiler,
            "-shared",
            "-o",
            "bin/lib/libtest_ada.so"
        ] + objects)
    except subprocess.CalledProcessError:
        success = False

    for obj in objects:
        try:
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
        except subprocess.CalledProcessError:
            success = False

    return success

def run(compiler, compiler_options, linker_options):
    sources = [
        'src/ada/records.ads',
    ]

    objects = []
    for src in sources:
        objects.append(src.split('/')[-1].replace(".ads", ".o"))

    success = build_objects(sources, compiler, compiler_options, linker_options)
    success = success and make_shared(objects, compiler)

    return success


if __name__ == '__main__':
    run()