# coding: utf8

"""t1_volume_longitudinal - Clinica Command Line Interface.
This file has been generated automatically by the `clinica generate template`
command line tool. See here for more details:
http://clinica.run/doc/InteractingWithClinica/
"""


import clinica.engine as ce

__author__ = "Emma Ducos"
#__copyright__ = "Copyright 2016-2018, The Aramis Lab Team"
#__credits__ = ["Jorge Samper Gonzalez"]
__license__ = "See LICENSE.txt file"
__version__ = "0.1.0"
__maintainer__ = "Emma Ducos"
__email__ = "emma.ducos@icm-institute.org"
__status__ = "Development"

class t1_volume_longitudinalCLI(ce.CmdParser):

    def define_name(self):
        """Define the sub-command name to run this pipeline.
        """
        self._name = 't1_volume_longitudinal'

    def define_description(self):
        """Define a description of this pipeline.
        """
        self._description = 'to do'

    def define_options(self):
        """Define the sub-command arguments
        """
        #mandatory arguments
        self._args.add_argument("bids_directory",
                                 help='Path to the BIDS directory.')
        self._args.add_argument("caps_directory",
                                 help='Path to the CAPS directory.')
        # self._args.add_argument("group_id",
        #                         help='User-defined identifier for the provided group of subjects.')

        #optional arguments
        # Add your own pipeline command line arguments here to be used in the
        # method below. Example below:
        #self._args.add_argument("-hw", "--hello_word_arg",
        #                        help='Word to say hello')
        # END OF EXAMPLE
        self._args.add_argument("-tsv", "--subjects_sessions_tsv",
                                 help='TSV file containing a list of subjects with their sessions.')
        self._args.add_argument("-wd", "--working_directory",
                                help='Temporary directory to store pipeline intermediate results')
        self._args.add_argument("-np", "--n_procs", type=int,
                                help='Number of cores used to run in parallel')
        self._args.add_argument("-v", "--verbose",
                                help='for debugging')

    def run_command(self, args):
        """
        """

        from tempfile import mkdtemp
        from clinica.pipelines.t1_volume_longitudinal.t1_volume_longitudinal_pipeline import t1_volume_longitudinal
        from nipype import config, logging

        # for debugging mode in the terminal
        config.enable_debug_mode()
        logging.update_logging(config)

        # instantiate pipeline with a BIDS and CAPS directory as inputs:
        # tsv file and caps_directory are optional
        pipeline = t1_volume_longitudinal(
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
            pipeline.config['execution']['crashfile_format'] = 'txt'  #crash files readable in .txt format
            pipeline.run()
            # to create a graph of the workflow
            pipeline.write_graph(graph2use='flat',
                                 dotfilename='/Users/emmaducos/Desktop/t1w_volume_longitudinal/working_directory/graph/graph_flat.dot')
            # pipeline.write_graph(graph2use='orig',
            #                      dotfilename='/Users/emmaducos/Desktop/t1w_volume_longitudinal/working_directory/graph/graph_orig.dot')
            # pipeline.write_graph(graph2use='exec',
            #                      dotfilename='/Users/emmaducos/Desktop/t1w_volume_longitudinal/working_directory/graph/graph_exec.dot')