"""
This script is intended to wake up every 30 min or so (eg via cron),
it checks for any new eprint papers via the OAI API and stashes
them into a sqlite database.
"""

import sys
import time
import random
import logging
import argparse
from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry, oai_dc_reader
from datetime import datetime

from aslite.db import get_papers_db, get_metas_db

URL = 'https://eprint.iacr.org/oai'

def parse_date_string(date_string: str) -> datetime:
    try:
       return datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S.%f%z')
    except ValueError:
       return datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S%z')

if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO, format='%(name)s %(levelname)s %(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    parser = argparse.ArgumentParser(description='eprint daemon')
    parser.add_argument('-n', '--num', type=int, default=100, help='up to how many papers to fetch')
    args = parser.parse_args()
    print(args)

    pdb = get_papers_db(flag='c')
    mdb = get_metas_db(flag='c')
    prevn = len(pdb)

    # fetch the latest papers
    total_updated = 0

    def store(p):
        pid = p['identifier'][0]
        print("Storing paper: {}".format(pid))
        pdb[pid] = p
        mdb[pid] = {'date': p['date'][0]}
        global total_updated
        total_updated += 1
    
    registry = MetadataRegistry()
    registry.registerReader('oai_dc', oai_dc_reader)
    client = Client(URL, registry)

    for i, record in enumerate(client.listRecords(metadataPrefix='oai_dc')):
        if record is None or record[1] is None:
            continue
        if i >= args.num:
            break
        
        header, metadata = record[0], record[1]
        metadata = metadata.__dict__['_map']

        # print(i, metadata)

        pid = metadata['identifier'][0]
        if pid in pdb:
            pts = parse_date_string(metadata['date'][1])
            old_pts = parse_date_string(pdb[pid]['date'][1])
            if pts > old_pts:
                # replace, this one is newer
                store(metadata)
        else:
            # new, simple store into database
            store(metadata)
    print("total updated: %d" % total_updated)
    sys.exit(0 if total_updated > 0 else 1)
