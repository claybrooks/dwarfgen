import argparse
import logging
import os
import sys
import json
import pymanifest
from .src import dwarfgen

ap = argparse.ArgumentParser()

ap.add_argument(
    '--to-idl',
    action='append',
    default=[],
    choices=['jidl'],
    help='IDL\'s to generate'
)

ap.add_argument(
    '--to-idl-dest',
    action='store',
    default=None,
    help='Full path to storage location of generated IDL\'s.  Required if --to-idl is set to a valid choice.'
)

ap.add_argument(
    '--idl-generator',
    action='append',
    default=[],
    nargs=2,
    metavar=("NAME", "PATH"),
    help='Full path to an IDL generator module.  Can be used with --to-idl'
)

ap.add_argument(
    '--to-lang',
    action='append',
    default=[],
    choices=['ada', 'c', 'c++', 'java', 'python']
)

ap.add_argument(
    '--to-lang-dest',
    action='store',
    default=None,
    help='Full path to storage location of generated code.  Sub folders will be generated to deliniate languages.'
)

ap.add_argument(
    '--lang-generator',
    action='append',
    default=[],
    nargs=2,
    metavar=("NAME", "PATH"),
    help='Full path to a language generator module.  Can be used with --to-lang'
)

pymanifest.add_args(ap)
args = ap.parse_args()

files = list(pymanifest.process_from_args(args))

failed = False
if files == []:
    logging.error("Must supply files to process, run 'python -m dwarfgen -h' for more help")
    failed = True

if args.to_idl == [] and args.to_lang == []:
    logging.error("Must supply --to-idl or --to-lang")
    failed = True

if args.to_idl != []:
    if args.to_idl_dest is None:
        logging.error("Must supply --to-idl-dest when supplying --to-idl")
        failed = True
    else:
        os.makedirs(args.to_idl_dest, exist_ok=True)

if args.to_lang != []:
    if args.to_lang_dest is None:
        logging.error("Must supply --to-lang-dest when supplying --to_lang")
        failed = True
    else:
        os.makedirs(args.to_lang_dest, exist_ok=True)

if failed:
    sys.exit(1)

ns = dwarfgen.process(files)

for idl in args.to_idl:
    if idl == 'jidl':
        jidl_json = {}
        ns.to_json(jidl_json)
        with open(os.path.join(args.to_idl_dest, 'jidl.json'), 'w+') as f:
            json.dump(jidl_json, f, indent=4)

for lang in args.to_lang:
    print ("{} not supported".format(lang))
