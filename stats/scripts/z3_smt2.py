#!/usr/bin/env python

import sys
import stats
import subprocess

def parseArgs (argv):
    import argparse as a
    p = a.ArgumentParser (description='Z3 Datalog Frontend')
    
    p.add_argument ('file', metavar='BENCHMARK', help='Benchmark file')
    p.add_argument ('--pp', 
                    help='Enable default pre-processing', 
                    action='store_true', default=False)
    p.add_argument ('--validate', help='Enable validation',
                    action='store_true', default=False)
    p.add_argument ('--trace', help='Trace levels to enable (spacer, pdr, dl,'
                                    'smt-relation, etc.)', 
                    default='')
    p.add_argument ('--answer', help='Print answer', action='store_true',
                    default=False)
    p.add_argument ('--engine', help='Datalog Engine (pdr/spacer)', default='spacer')
    p.add_argument ('--verbose', help='Z3 verbosity', default=0)
    p.add_argument ('--use-utvpi', dest='use_utvpi', help='use utvpi/diff-logic '
                                                          'solvers, if applicable',
                    action='store_true', default=False)
    p.add_argument ('--eager-reach-check', dest='eager_reach_check',
                    help='eagerly use reachability facts for every local query',
                    action='store_true', default=False)
    p.add_argument ('--from-lvl', dest='from_lvl',
                    type=int,
                    help='start level for query predicate',
                    action='store', default=0)
    p.add_argument ('--print-stats', dest='print_stats',
                    help='flag to print stats',
                    action='store_true', default=False)
    p.add_argument ('--dfs', dest='dfs',
                    help='use dfs instead of bfs',
                    action='store_true', default=False)
    p.add_argument ('--order-children', dest='order_children',
                    help='0 (rtol), 1 (ltor)', default=0)

    return p.parse_args (argv)

def stat (key, val): stats.put (key, val)

def main (argv):
    args = parseArgs (argv[1:])
    stat ('Result', 'UNKNOWN')

    if 'z3' in os.listdir('.') and os.path.isfile ('z3'):
        z3_args = os.getcwd () + '/z3'
        print 'Using z3 at :', z3_args
    else:
        print 'Assuming z3 is in the executable path'
        z3_args = 'z3'

    z3_args += ' -v:' + str(args.verbose)

    if not args.pp:
        print 'No pre-processing'
        z3_args += ' fixedpoint.slice=false'
        z3_args += ' fixedpoint.inline_linear=false'
        z3_args += ' fixedpoint.inline_eager=false'

    print 'Engine: ', args.engine

    if (args.validate):
        z3_args += ' fixedpoint.validate_result=true'
    else:
        z3_args += ' fixedpoint.validate_result=false'

    if (args.answer):
        z3_args += ' fixedpoint.print_answer=true'

    z3_args += ' fixedpoint.engine='
    z3_args += args.engine


    z3_args += ' fixedpoint.use_farkas=true'
    z3_args += ' fixedpoint.generate_proof_trace=false'

    if args.use_utvpi:
        z3_args += ' fixedpoint.use_utvpi=true'
    else:
        z3_args += ' fixedpoint.use_utvpi=false'

    if args.eager_reach_check:
        z3_args += ' fixedpoint.eager_reach_check=true'
    else:
        z3_args += ' fixedpoint.eager_reach_check=false'

    if args.print_stats:
        z3_args += ' -st'

    if args.dfs:
        z3_args += ' fixedpoint.bfs_model_search=false'

    if int(args.order_children)==1:
        z3_args += ' fixedpoint.order_children=1'

    z3_args += ' ' + args.file


    if len(args.trace) > 0:
        print 'Enable trace: ',
        for t in args.trace.split (':'):
            print t,
            z3_args += ' -tr:{}'.format (t)
        print 
        stats.put ('Trace', args.trace)

    print z3_args

    with stats.timer ('Query'):
        popen = subprocess.Popen(z3_args.split (), stdout=subprocess.PIPE)
        popen.wait()
        res = popen.stdout.read()
    res = res[:-1] # strip off the newline
    if res.startswith ('sat'):
        res = 'sat'
    elif res.startswith ('unsat'):
        res = 'unsat'
    else:
        res = 'unknown'
    print 'Result:', res

    if res == 'sat': stat ('Result', 'SAFE')
    elif res == 'unsat': stat ('Result', 'CEX')
    
if __name__ == '__main__':
    try:
        res = main (sys.argv)
    finally:
        stats.brunch_print ()
    sys.exit (res)

