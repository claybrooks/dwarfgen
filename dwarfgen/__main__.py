import argparse
import logging
import os
import sys
import pymanifest

ap = argparse.ArgumentParser()

ap.add_argument(
    '--output-idl-dest',
    action='store',
    default=None,
    help='Full path to storage location of generated IDL\'s.  Required if --to-idl is set to a valid choice.'
)

ap.add_argument(
    '--to-idl',
    action='append',
    default=[],
    choices=['jidl'],
    help='IDL\'s to generate'
)

ap.add_argument(
    '--output-lang-dest',
    action='store',
    default=None,
    help='Full path to storage location of generated code.  Sub folders will be generated to deliniate languages.'
)

ap.add_argument(
    '--to-lang',
    action='append',
    default=[],
    choices=['ada', 'c', 'c++', 'java', 'python']
)

ap.add_argument('--idl-generator',
    action='append',
    default=[],
    nargs=2,
    metavar=("NAME", "PATH"),
    help='Full path to an IDL generator module.  Can be used with --to-idl'
)

ap.add_argument(
    '--lang-generator',
    action='append',
    default=[],
    nargs=2,
    metavar=("NAME", "PATH"),
    help='Full path to a language generator module.  Can be used with --to-lang'
)

ap.add_argument(
    '--ignore-missing-entries',
    default=False,
    action='store_true',
    help='If specified, missing entries from --object, --object-dir, --ignore-object, --ignore-object-dir, and contents'\
         ' from --object-file and --ignore-object-file will be treated as warnings instead of errors'
)

pymanifest.add_args(ap)
args = ap.parse_args()

if args.to_idl is [] and args.to_lang is []:
    logging.error("Must supply --to-idl or --to-lang, else what am I supposed to do?")
    sys.exit(-1)

files = pymanifest.process_from_args(args)