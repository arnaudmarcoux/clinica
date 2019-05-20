"""t1_volume_longitudinal - Clinica Pipeline.
This file has been generated automatically by the `clinica generate template`
command line tool. See here for more details: https://gitlab.icm-institute.org/aramislab/clinica/wikis/docs/InteractingWithClinica.
"""

# WARNING: Don't put any import statement here except if it's absolutly
# necessary. Put it *inside* the different methods.
# Otherwise it will slow down the dynamic loading of the pipelines list by the
# command line tool.
import clinica.pipelines.engine as cpe

__author__ = "Emma Ducos"
__copyright__ = "Copyright 2016-2018, The Aramis Lab Team"
__credits__ = ["Jorge Samper Gonzalez"]
__license__ = "See LICENSE.txt file"
__version__ = "0.1.0"
__maintainer__ = "Emma Ducos"
__email__ = "emma.ducos@icm-institute.org"
__status__ = "Development"


class T1VolumeLongitudinal(cpe.Pipeline):
    """t1_volume_longitudinal SHORT DESCRIPTION.

    Args:
        input_dir: A BIDS directory.
        output_dir: An empty output directory where CAPS structured data will be written.
        subjects_sessions_list: The Subjects-Sessions list file (in .tsv format).

    Returns:
        A clinica pipeline object containing the t1_volume_longitudinal pipeline.

    """

    def check_custom_dependencies(self):
        """Check dependencies that can not be listed in the `info.json` file.
        """
        from os.path import join, exists, expandvars
        if not exists(expandvars('$SPM_HOME')):
            raise RuntimeError('Var $SPM_HOME not found in your envrionnement. Is SPM installed properly ?')
        else:
            if not exists(join(expandvars('$SPM_HOME'), 'toolbox', 'cat12')):
                raise RuntimeError('cat12 folder not found in your SPM installation in ' + expandvars('$SPM_HOME'))
            if not exists(join(expandvars('$SPM_HOME'), 'toolbox', 'LST')):
                raise RuntimeError('LST (Lesion Segmentation Toolbox) folder not found in your SPM installation in ' + expandvars('$SPM_HOME'))


    def get_input_fields(self):
        """Specify the list of possible inputs of this pipeline.

        Returns:
            A list of (string) input fields name.
        """

        return [
            'sesbaseline_T1w',
            'seslast_T1w',
            'deltaTime',
            'sesbaseline_FLAIR',
            'seslast_FLAIR'
        ]

    def get_output_fields(self):
        """Specify the list of possible outputs of this pipeline.

        Returns:
            A list of (string) output fields name.
        """

        return ['rdartel_c1h', 'rdartel_c2h', 'rdartel_c3', 'rdartel_avgT1w']

    def build_input_node(self):
        """Build and connect an input node to the pipeline.
        We iterate over subjects to get all the files needed to run the pipeline
        """

        import nipype.interfaces.utility as nutil
        import nipype.pipeline.engine as npe
        import clinica.pipelines.t1_volume_longitudinal.t1_volume_longitudinal_utils as utils

        # instantiating the data grabber node
        read_node = npe.Node(name="read_node",
                             interface=nutil.IdentityInterface(fields=self.get_input_fields(),
                                                               mandatory_inputs=True),
                             synchronize=True)

        # forcing the variables subject, sesbaseline, seslast and modality to the values of the first
        # subject of the cohort, for test purposes
        # careful with self.subjects, because of several "same" subject names
        subject_selected = ['0040043MACL']  # self.subjects[0]
        # session_selected = ['sesbaseline','seslast'] #self.sessions
        sesbaseline = ['M00']
        seslast = ['M24']

        # inputs of the read_node
        # getting the T1w images at ses-M00 and ses-M24
        modality_selected = "T1w"
        read_node.inputs.sesbaseline_T1w = list(utils.select_bids_images(subject_selected,
                                                                         sesbaseline,
                                                                         modality_selected,
                                                                         self.bids_layout))
        read_node.inputs.seslast_T1w = list(utils.select_bids_images(subject_selected,
                                                                     seslast,
                                                                     modality_selected,
                                                                     self.bids_layout))
        # getting the FLAIR images at ses-M00 and ses-M24
        modality_selected = "FLAIR"
        read_node.inputs.sesbaseline_FLAIR = list(utils.select_bids_images(subject_selected,
                                                                           sesbaseline,
                                                                           modality_selected,
                                                                           self.bids_layout))
        read_node.inputs.seslast_FLAIR = list(utils.select_bids_images(subject_selected,
                                                                       seslast,
                                                                       modality_selected,
                                                                       self.bids_layout))
        # getting the deltaTime variable from the 'participants.json' file
        read_node.inputs.deltaTime = utils.select_deltaTime(subject_selected, self.bids_directory)

        # connect data grabber to input
        self.connect([
            (read_node, self.input_node, [('sesbaseline_T1w', 'sesbaseline_T1w'),
                                          ('seslast_T1w', 'seslast_T1w'),
                                          ('deltaTime', 'deltaTime'),
                                          ('sesbaseline_FLAIR', 'sesbaseline_FLAIR'),
                                          ('seslast_FLAIR', 'seslast_FLAIR'),
                                          ])
        ])


        # Replace by T1w-series, Flair-series, & mapnodes...
        # NOT WORKING YET (but almost)
        subjects, sessions = utils.regroup_subjects_sessions(self.subjects,
                                                             self.sessions)

        read_node = npe.Node(name="read_node",
                             interface=nutil.IdentityInterface(
                                 fields=['t1w', 'flair', 'delta'],
                                 mandatory_inputs=True),
                             synchronize=True)

        read_node.inputs.t1w = utils.get_t1w(subjects, sessions, self.bids_directory)
        #read_node.inputs.flair = utils.get_flair(subjects, sessions)
        #read_node.inputs.delta = utils.get_delta(subjects, sessions)


    def build_output_node(self):
        """Build and connect an output node to the pipeline.
        """

        import nipype.pipeline.engine as npe
        import nipype.interfaces.io as nio

        # DataSink configuration
        datasink_infields = self.get_output_fields()
        datasink_connections = [
            ('rdartel_c1h', 'rdartel_c1h'),
            ('rdartel_c2h', 'rdartel_c2h'),
            ('rdartel_c3', 'rdartel_c3'),
            ('rdartel_avgT1w', 'rdartel_avgT1w')
        ]
        datasink_iterfields = datasink_infields
        sinker = npe.MapNode(name='sinker',
                             iterfield=datasink_iterfields,
                             interface=nio.DataSink(infields=datasink_infields))
        sinker.inputs.base_directory = self.caps_directory  # Name of the output folder
        sinker.inputs.parametrization = False

        # connecting the datasink to the output node
        self.connect([
            (self.output_node, sinker, datasink_connections)
        ])

    def build_core_nodes(self):
        """Build and connect the core nodes of the pipeline.
        """
        import os
        import nipype.pipeline.engine as npe
        import nipype.interfaces.spm as spm
        import nipype.interfaces.utility as niu
        import clinica.pipelines.t1_volume_longitudinal.t1_volume_longitudinal_utils as utils
        from nipype.interfaces import fsl

        serialLongitudinalRegistration_nd = npe.Node(niu.Function(input_names=['sesbaseline_image',
                                                                               'seslast_image',
                                                                               'deltaTime',
                                                                               'nameOfNode',
                                                                               'matlab_path'],
                                                                  output_names=['avg',
                                                                                'defField_sesbaseline',
                                                                                'defField_seslast'],
                                                                  function=utils.runSerialLongitudinalRegistration),
                                                     name='serialLongitudinalRegistration')
        serialLongitudinalRegistration_nd.inputs.matlab_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
        # applied to T1w images
        serialLongitudinalRegistration_T1w_nd = serialLongitudinalRegistration_nd.clone(
            'serialLongitudinalRegistration_T1w')
        serialLongitudinalRegistration_T1w_nd.inputs.nameOfNode = 'T1w'
        # applied to FLAIR images
        serialLongitudinalRegistration_FLAIR_nd = serialLongitudinalRegistration_nd.clone(
            'serialLongitudinalRegistration_FLAIR')
        serialLongitudinalRegistration_FLAIR_nd.inputs.nameOfNode = 'FLAIR'

        newSegmentSPM12_nd = npe.MapNode(spm.NewSegment(),
                                         name='newSegmentSPM12',
                                         iterfield=['channel_files'])
        newSegmentSPM12_nd.inputs.affine_regularization = 'mni'
        newSegmentSPM12_nd.inputs.channel_info = (0.001, 60, (False, False))
        newSegmentSPM12_nd.inputs.sampling_distance = 3
        newSegmentSPM12_nd.inputs.warping_regularization = [0, 0.001, 0.5, 0.05, 0.2]
        newSegmentSPM12_nd.inputs.write_deformation_fields = [False, False]
        tpmnii = os.path.join(os.path.expandvars('$SPM_HOME'), 'tpm', 'TPM.nii')
        tissue1 = ((tpmnii, 1), 1, (False, False), (False, False))
        tissue2 = ((tpmnii, 2), 1, (False, False), (False, False))
        tissue3 = ((tpmnii, 3), 2, (True, False), (False, False))
        tissue4 = ((tpmnii, 4), 3, (True, False), (False, False))
        tissue5 = ((tpmnii, 5), 4, (True, False), (False, False))
        tissue6 = ((tpmnii, 5), 2, (True, False), (False, False))
        newSegmentSPM12_nd.inputs.tissues = [tissue1, tissue2, tissue3, tissue4, tissue5, tissue6]

        # Segmentation CAT12
        # ======================================
        # TODO: swap time.sleep(300) with a subprocess solution ;
        # from avg_T1w to get c1 and c2 compartment segmentation
        # wrap a matlab SPM12 job script

        segmentCAT12_nd = npe.Node(niu.Function(input_names=['image',
                                                             'nameOfNode',
                                                             'matlab_path'],
                                                output_names=['c1', 'c2'],
                                                function=utils.runSegmentCAT12),
                                   name='segmentCAT12')
        segmentCAT12_nd.inputs.matlab_path = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
        # applied on ses-baseline images
        segmentCAT12sesbaseline_nd = segmentCAT12_nd.clone('segmentCAT12sesbaseline')
        segmentCAT12sesbaseline_nd.inputs.nameOfNode = 'sesbaseline'
        # applied on ses-last images
        segmentCAT12seslast_nd = segmentCAT12_nd.clone('segmentCAT12seslast')
        segmentCAT12seslast_nd.inputs.nameOfNode = 'seslast'
        # applied on avg images
        segmentCAT12avg_nd = segmentCAT12_nd.clone('segmentCAT12avg')
        segmentCAT12avg_nd.inputs.nameOfNode = 'avg'

        # Segmentation FSL FIRST
        # ===============================
        # from avg_T1w get a _all_fast_firstseg.nii.gz file to compute a more precise white matter compartment
        # uses the nipype fsl interface FIRST
        segmentFsl_nd = npe.MapNode(fsl.FIRST(),
                                    name='segmentFsl',
                                    iterfield=['in_file'])

        segmentFsl_nd.inputs.out_file = 'avg_centered_' + self.subjects[0] + '_T1w'  # carefull with self.subjects
        segmentFsl_nd.inputs.method = 'fast'

        # lesion segmentation toolbox
        # ===============================
        # TODO: pipelineFolder var
        LSTLGA_nd = npe.Node(niu.Function(input_names=['avg_T1w', 'avg_FLAIR', 'pipelineFolder'],

                                          output_names=['lesion_map'],
                                          function=utils.runLesionSegmentationToolboxLGA),
                             name='LSTLGA')
        LSTLGA_nd.inputs.pipelineFolder = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))

        # image calculator in SPM12
        # ===================================
        # wrap a matlabbatch SPM12 job script
        imCalc_nd = npe.Node(niu.Function(input_names=['c1', 'c2',
                                                       'native_class_images', 'segmentation_file', 'lesion_map',
                                                       'output',
                                                       'expression',
                                                       'pipelineFolder', 'nameOfNode'],
                                          output_names=['binary_mask'],
                                          function=utils.runImCalc),
                             name='imCalc')
        # create c1
        imCalc_c1_nd = imCalc_nd.clone('imCalc_c1')
        imCalc_c1_nd.inputs.output = 'c1bin_avg_T1w'  # carefull with self.subjects
        imCalc_c1_nd.inputs.expression = '(((i1>i2).*(i1>i3).*(i1>i4).*(i1>i5).*(i1>i6))-i7)'
        imCalc_c1_nd.inputs.pipelineFolder = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
        imCalc_c1_nd.inputs.nameOfNode = 'c1'
        imCalc_c1_nd.inputs.segmentation_file = None
        # create c2
        imCalc_c2_nd = imCalc_nd.clone('imCalc_c2')
        imCalc_c2_nd.inputs.output = 'c2bin_avg_T1w'  # carefull with self.subjects
        imCalc_c2_nd.inputs.expression = '(((i2>i1).*(i2>i3).*(i2>i4).*(i2>i5).*(i2>i6))-i7)>0'
        imCalc_c2_nd.inputs.pipelineFolder = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
        imCalc_c2_nd.inputs.nameOfNode = 'c2'
        imCalc_c2_nd.inputs.segmentation_file = None
        # create c3
        imCalc_c3_nd = imCalc_nd.clone('imCalc_c3')
        imCalc_c3_nd.inputs.output = 'c3bin_avg_T1w'  # carefull with self.subjects
        imCalc_c3_nd.inputs.expression = '(((i3>i1).*(i3>i2).*(i3>i4).*(i3>i5).*(i3>i6)-i7)>0)'
        imCalc_c3_nd.inputs.pipelineFolder = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
        imCalc_c3_nd.inputs.nameOfNode = 'c3'
        imCalc_c3_nd.inputs.segmentation_file = None
        # create c4
        imCalc_c4_nd = imCalc_nd.clone('imCalc_c4')
        imCalc_c4_nd.inputs.output = 'c4bin_avg_T1w'  # carefull with self.subjects
        imCalc_c4_nd.inputs.expression = '(i4>i1).*(i4>i2).*(i4>i3).*(i4>i5).*(i4>i6)'
        imCalc_c4_nd.inputs.pipelineFolder = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
        imCalc_c4_nd.inputs.nameOfNode = 'c4'
        imCalc_c4_nd.inputs.segmentation_file = None
        imCalc_c4_nd.inputs.lesion_map = None
        # create c5
        imCalc_c5_nd = imCalc_nd.clone('imCalc_c5')
        imCalc_c5_nd.inputs.output = 'c5bin_avg_T1w'  # carefull with self.subjects
        imCalc_c5_nd.inputs.expression = '(i5>i1).*(i5>i2).*(i5>i3).*(i5>i4).*(i5>i6)'
        imCalc_c5_nd.inputs.pipelineFolder = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
        imCalc_c5_nd.inputs.working_directory = self.base_dir
        imCalc_c5_nd.inputs.nameOfNode = 'c5'
        imCalc_c5_nd.inputs.segmentation_file = None
        imCalc_c5_nd.inputs.lesion_map = None
        # create c6
        imCalc_c6_nd = imCalc_nd.clone('imCalc_c6')
        imCalc_c6_nd.inputs.output = 'c6bin_avg_' + self.subjects[0] + '_T1w'  # carefull with self.subjects
        imCalc_c6_nd.inputs.expression = '(i6>i1).*(i6>i2).*(i6>i3).*(i6>i4).*(i6>i5)'
        imCalc_c6_nd.inputs.pipelineFolder = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
        imCalc_c6_nd.inputs.working_directory = self.base_dir
        imCalc_c6_nd.inputs.nameOfNode = 'c6'
        imCalc_c6_nd.inputs.segmentation_file = None
        imCalc_c6_nd.inputs.lesion_map = None
        # create c1 hybrid
        imCalc_c1h_nd = imCalc_nd.clone('imCalc_c1h')
        imCalc_c1h_nd.inputs.output = 'c1hyb_avg_T1w'  # carefull with self.subjects
        imCalc_c1h_nd.inputs.expression = \
            '(i1+(((i2<13.1).*(i2>9.9))+((i2<26.1).*(i2>25.9))+((i2<52.1).*(i2>48.9))+((i2<58.1).*(i2>57.9))))>0'
        imCalc_c1h_nd.inputs.pipelineFolder = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
        imCalc_c1h_nd.inputs.working_directory = self.base_dir
        imCalc_c1h_nd.inputs.nameOfNode = 'c1h'
        imCalc_c1h_nd.inputs.c2 = None
        imCalc_c1h_nd.inputs.native_class_images = None
        imCalc_c1h_nd.inputs.lesion_map = None
        # create c2 hybrid
        imCalc_c2h_nd = imCalc_nd.clone('imCalc_c2h')
        imCalc_c2h_nd.inputs.output = 'c2hyb_avg_' + self.subjects[0] + '_T1w'  # carefull with self.subjects
        imCalc_c2h_nd.inputs.expression = '(i2-i1)>0'
        imCalc_c2h_nd.inputs.pipelineFolder = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
        imCalc_c2h_nd.inputs.working_directory = self.base_dir
        imCalc_c2h_nd.inputs.nameOfNode = 'c2h'
        imCalc_c2h_nd.inputs.native_class_images = None
        imCalc_c2h_nd.inputs.lesion_map = None
        imCalc_c2h_nd.inputs.segmentation_file = None

        # Segmentation SPM12 old
        # ===============================
        # from avg_T1w get a seg_sn.mat file for spatial normalization
        # uses nipype spm interface Segment
        # inputs extracted from a SPM12 matlabbatch script
        oldSegmentSPM12_nd = npe.MapNode(spm.Segment(),
                                         name='oldSegmentSPM12',
                                         iterfield=['data'])
        oldSegmentSPM12_nd.inputs.wm_output_type = [False, False, False]
        oldSegmentSPM12_nd.inputs.gm_output_type = [False, False, False]
        oldSegmentSPM12_nd.inputs.csf_output_type = [False, False, False]
        oldSegmentSPM12_nd.inputs.affine_regularization = 'mni'
        oldSegmentSPM12_nd.inputs.save_bias_corrected = True
        oldSegmentSPM12_nd.inputs.bias_regularization = 0.0001
        oldSegmentSPM12_nd.inputs.warping_regularization = 1
        oldSegmentSPM12_nd.inputs.sampling_distance = 3
        oldSegmentSPM12_nd.inputs.gaussians_per_class = [2, 2, 2, 4]
        oldSegmentSPM12_nd.inputs.warp_frequency_cutoff = 25
        oldSegmentSPM12_nd.inputs.bias_fwhm = 60

        def_snmat_nd = npe.Node(niu.Function(input_names=['snmat', 'c1h', 'c2h', 'c3', 'avg_T1w',
                                                          'pipelineFolder'
                                                          ],
                                             output_names=['rdartel_c1h', 'rdartel_c2h',
                                                           'rdartel_c3', 'rdartel_avgT1w'],
                                             function=utils.runDeformationSnmat),
                                name='deformationSnmat')
        def_snmat_nd.inputs.pipelineFolder = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))


        # Connection
        # ==========

        self.connect([
            (self.input_node, serialLongitudinalRegistration_T1w_nd, [('sesbaseline_T1w', 'sesbaseline_image')]),
            (self.input_node, serialLongitudinalRegistration_T1w_nd, [('seslast_T1w', 'seslast_image')]),
            (self.input_node, serialLongitudinalRegistration_T1w_nd, [('deltaTime', 'deltaTime')]),
            (self.input_node, serialLongitudinalRegistration_FLAIR_nd, [('sesbaseline_FLAIR', 'sesbaseline_image')]),
            (self.input_node, serialLongitudinalRegistration_FLAIR_nd, [('seslast_FLAIR', 'seslast_image')]),
            (self.input_node, serialLongitudinalRegistration_FLAIR_nd, [('deltaTime', 'deltaTime')]),

            (self.input_node, segmentCAT12sesbaseline_nd, [('sesbaseline_T1w', 'image')]),
            (self.input_node, segmentCAT12seslast_nd, [('seslast_T1w', 'image')]),
            (serialLongitudinalRegistration_T1w_nd, segmentCAT12avg_nd, [('avg', 'image')]),

            (serialLongitudinalRegistration_T1w_nd, newSegmentSPM12_nd, [('avg', 'channel_files')]),
            (serialLongitudinalRegistration_T1w_nd, segmentFsl_nd, [('avg', 'in_file')]),
            (serialLongitudinalRegistration_T1w_nd, oldSegmentSPM12_nd, [('avg', 'data')]),

            (serialLongitudinalRegistration_T1w_nd, LSTLGA_nd, [('avg', 'avg_T1w')]),
            (serialLongitudinalRegistration_FLAIR_nd, LSTLGA_nd, [('avg', 'avg_FLAIR')]),

            (segmentCAT12avg_nd, imCalc_c1_nd, [('c1', 'c1')]),
            (segmentCAT12avg_nd, imCalc_c1_nd, [('c2', 'c2')]),
            (newSegmentSPM12_nd, imCalc_c1_nd, [('native_class_images', 'native_class_images')]),
            (LSTLGA_nd, imCalc_c1_nd, [('lesion_map', 'lesion_map')]),

            (segmentCAT12avg_nd, imCalc_c2_nd, [('c1', 'c1')]),
            (segmentCAT12avg_nd, imCalc_c2_nd, [('c2', 'c2')]),
            (newSegmentSPM12_nd, imCalc_c2_nd, [('native_class_images', 'native_class_images')]),
            (LSTLGA_nd, imCalc_c2_nd, [('lesion_map', 'lesion_map')]),

            (segmentCAT12avg_nd, imCalc_c3_nd, [('c1', 'c1')]),
            (segmentCAT12avg_nd, imCalc_c3_nd, [('c2', 'c2')]),
            (newSegmentSPM12_nd, imCalc_c3_nd, [('native_class_images', 'native_class_images')]),
            (LSTLGA_nd, imCalc_c3_nd, [('lesion_map', 'lesion_map')]),

            (segmentCAT12avg_nd, imCalc_c4_nd, [('c1', 'c1')]),
            (segmentCAT12avg_nd, imCalc_c4_nd, [('c2', 'c2')]),
            (newSegmentSPM12_nd, imCalc_c4_nd, [('native_class_images', 'native_class_images')]),

            (segmentCAT12avg_nd, imCalc_c5_nd, [('c1', 'c1')]),
            (segmentCAT12avg_nd, imCalc_c5_nd, [('c2', 'c2')]),
            (newSegmentSPM12_nd, imCalc_c5_nd, [('native_class_images', 'native_class_images')]),

            (segmentCAT12avg_nd, imCalc_c6_nd, [('c1', 'c1')]),
            (segmentCAT12avg_nd, imCalc_c6_nd, [('c2', 'c2')]),
            (newSegmentSPM12_nd, imCalc_c6_nd, [('native_class_images', 'native_class_images')]),

            (imCalc_c1_nd, imCalc_c1h_nd, [('binary_mask', 'c1')]),
            (segmentFsl_nd, imCalc_c1h_nd, [('segmentation_file', 'segmentation_file')]),

            (imCalc_c1h_nd, imCalc_c2h_nd, [('binary_mask', 'c1')]),
            (imCalc_c2_nd, imCalc_c2h_nd, [('binary_mask', 'c2')]),

            (oldSegmentSPM12_nd, def_snmat_nd, [('transformation_mat', 'snmat')]),
            (imCalc_c1h_nd, def_snmat_nd, [('binary_mask', 'c1h')]),
            (imCalc_c2h_nd, def_snmat_nd, [('binary_mask', 'c2h')]),
            (imCalc_c3_nd, def_snmat_nd, [('binary_mask', 'c3')]),
            (serialLongitudinalRegistration_T1w_nd, def_snmat_nd, [('avg', 'avg_T1w')]),

            (def_snmat_nd, self.output_node, [('rdartel_c1h', 'rdartel_c1h')]),
            (def_snmat_nd, self.output_node, [('rdartel_c2h', 'rdartel_c2h')]),
            (def_snmat_nd, self.output_node, [('rdartel_c3', 'rdartel_c3')]),
            (def_snmat_nd, self.output_node, [('rdartel_avgT1w', 'rdartel_avgT1w')])
        ])
