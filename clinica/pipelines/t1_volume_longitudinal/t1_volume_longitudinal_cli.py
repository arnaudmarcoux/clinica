# coding: utf8

"""t1_volume_longitudinal - Clinica Command Line Interface.
This file has been generated automatically by the `clinica generate template`
command line tool. See here for more details:
http://clinica.run/doc/InteractingWithClinica/
"""


import clinica.engine as ce

__author__ = "Emma Ducos"
__license__ = "See LICENSE.txt file"
__version__ = "0.1.0"
__maintainer__ = "Emma Ducos"
__email__ = "emma.ducos@icm-institute.org"
__status__ = "Development"

class t1_volume_longitudinalCLI(ce.CmdParser):

    def define_name(self):
        """Define the sub-command name to run this pipeline.
        """
        self._name = 't1-volume-longitudinal'

    def define_description(self):
        """Define a description of this pipeline.
        """
        # TODO fill description
        self._description = 'INSERT PIPELINE DESCRIPTION'

    def define_options(self):
        """Define the sub-command arguments
        """
        from clinica.engine.cmdparser import PIPELINE_CATEGORIES

        #mandatory arguments
        clinica_comp = self._args.add_argument_group(PIPELINE_CATEGORIES['CLINICA_COMPULSORY'])
        clinica_comp.add_argument("bids_directory",
                                  help='Path to the BIDS directory.')
        clinica_comp.add_argument("caps_directory",
                                  help='Path to the CAPS directory.')

        clinica_comp = self._args.add_argument_group(PIPELINE_CATEGORIES['CLINICA_OPTIONAL'])
        clinica_comp.add_argument("-tsv", "--subjects_sessions_tsv",
                                  help='TSV file containing a list of subjects with their sessions.')
        clinica_comp.add_argument("-wd", "--working_directory",
                                  help='Temporary directory to store pipeline intermediate results')
        clinica_comp.add_argument("-np", "--n_procs", type=int,
                                  help='Number of cores used to run in parallel')
        clinica_comp.add_argument("-v", "--verbose",
                                  help='for debugging')

    def run_command(self, args):
        from os.path import join
        from tempfile import mkdtemp
        from clinica.pipelines.t1_volume_longitudinal.t1_volume_longitudinal_pipeline import T1VolumeLongitudinal

        # instantiate pipeline with a BIDS and CAPS directory as inputs:
        # tsv file and caps_directory are optional
        pipeline = T1VolumeLongitudinal(
             bids_directory=self.absolute_path(args.bids_directory),
             caps_directory=self.absolute_path(args.caps_directory),
             tsv_file=self.absolute_path(args.subjects_sessions_tsv))

        if args.working_directory is None:
            args.working_directory = mkdtemp()
        pipeline.base_dir = self.absolute_path(args.working_directory)

        if args.n_procs:
            pipeline.run(plugin='MultiProc',
                         plugin_args={'n_procs': args.n_procs})
        else:
            pipeline.run()
            # to create a graph of the workflow
            # TODO not forget to remove the following line when publishing pipeline (write_graph needs a non mandatory library to run)
            pipeline.write_graph(graph2use='flat', dotfilename=join(pipeline.caps_directory, 'graph_flat.dot'))