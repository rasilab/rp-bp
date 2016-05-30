#! /usr/bin/env python3

import argparse
import yaml

import misc.utils as utils
import misc.slurm as slurm

default_num_procs = 2

default_peptide_separator = '\t'
default_peptide_filter_field = 'PEP'
default_peptide_filter_value = 0.1

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="This script identifies the orf peptide matches for all samples in "
        "a project.")
    parser.add_argument('config', help="The (yaml) config file")
    parser.add_argument('peptides', help="The peptides.txt file produced by MaxQuant")
    
    parser.add_argument('--peptide-filter-field', help="The field to use for filtering "
        "the peptides from MaxQuant", default=default_peptide_filter_field)
    parser.add_argument('--peptide-filter-value', help="All peptides with a value greater "
        "than the filter value will be removed", type=float, default=default_peptide_filter_value)

    parser.add_argument('--peptide-separator', help="The separator in the --peptide file",
        default=default_peptide_separator)

    slurm.add_sbatch_options(parser)
    utils.add_logging_options(parser)
    args = parser.parse_args()
    utils.update_logging(args)
    
    logging_str = utils.get_logging_options_string(args)

    config = yaml.load(open(args.config))
    call = not args.do_not_call

    programs = [
        'get-orf-peptide-matches'
    ]
    utils.check_programs_exist(programs)

    required_keys = [
        'riboseq_data'
    ]
    utils.check_keys_exist(config, required_keys)

    note_str = config.get('note', None)
    args_dict = vars(args)

    peptide_filter_field_str = utils.get_config_argument(args_dict, 'peptides_filter_field')
    peptide_filter_value_str = utils.get_config_argument(args_dict, 'peptides_filter_value')
    peptide_separator_str = utils.get_config_argument(args_dict, 'peptide_separator')

    num_procs_str = utils.get_config_argument(args_dict, 'num_cpus', 'num-procs')
    
    for name, data in config['riboseq_samples'].items():
        
        ### bf predictions

        predicted_proteins = filenames.get_riboseq_predicted_orfs_protein(
            config['riboseq_data'], args.name, length=lengths, offset=offsets, 
            is_unique=True, note=note_str)

        peptide_matches = filenames.get_riboseq_peptide_matches(
            config['riboseq_data'], args.name, length=lengths, offset=offsets, 
            is_unique=True, note=note_str)

        cmd = "get-orf-peptide-matches {} {} {} {} {} {} {} {}".format(predicted_proteins, 
            args.peptides, peptide_matches, num_procs_str, peptide_filter_field_str, 
            peptide_filter_value_str, peptide_separator_str, logging_str)

        slurm.check_sbatch(cmd, args=args)

        ### chisq predictions

        predicted_chisq_protein = filenames.get_riboseq_predicted_orfs_protein(
            config['riboseq_data'], args.name, length=lengths, offset=offsets, 
            is_unique=True, note=note_str, is_chisq=True)

        chisq_peptide_matches = filenames.get_riboseq_peptide_matches(
            config['riboseq_data'], args.name, length=lengths, offset=offsets, 
            is_unique=True, note=note_str, is_chisq=True)

        cmd = "get-orf-peptide-matches {} {} {} {} {} {} {} {}".format(predicted_chisq_proteins, 
            args.peptides, chisq_peptide_matches, num_procs_str, peptide_filter_field_str, 
            peptide_filter_value_str, peptide_separator_str, logging_str)

        slurm.check_sbatch(cmd, args=args)

if __name__ == '__main__':
    main()