# coding: utf8

"""t1_volume_longitudinal - Clinica Utilities.
This file has been generated automatically by the `clinica generate template`
command line tool. See here for more details:
http://clinica.run/doc/InteractingWithClinica/
"""

__author__ = "Emma Ducos"
__copyright__ = "Copyright 2016-2018, The Aramis Lab Team"
__credits__ = ["Jorge Samper Gonzalez"]
__license__ = "See LICENSE.txt file"
__version__ = "0.1.0"
__maintainer__ = "Emma Ducos"
__email__ = "emma.ducos@icm-institute.org"
__status__ = "Development"

def select_bids_images(subjects, sessions, image_type, bids_layout):
    """
    select the images that verify sessions and image_type for all the subjects in the bids dataset
    :param subjects: list of the subjects ids (string). ex: ['0040043MACL', '0040044BERE']
    :param sessions: list of the sessions ids (string). ex: ['M00', 'M24']
    :param image_type: name of the modality selected (string). ex: 'T1w'
    :param bids_layout: self.bids_layout from t1_volume_longitudinal_pipeline.py
    :return list of images per subjects.
    """
    if len(subjects) != len(sessions):
       raise RuntimeError("Subjects list and sessions list must have the same length.")

    return [select_image(subjects[i], sessions[i], image_type, bids_layout) for i in range(len(subjects))]


def select_image(participant_id, session_id, image_type, bids_layout):
    """
    starting from the tsv with the participant_id and the session_id look for the corresponding image in the bids directory
    """
    import warnings

    if participant_id.startswith('sub-'):
        participant_id = participant_id[4:]
    if session_id.startswith('ses-'):
        session_id = session_id[4:]

    selected_images = bids_layout.get(subject=participant_id, session=session_id, type=image_type,
                                      return_type='file', extensions='nii.gz')
    if len(selected_images) == 0:
        selected_images = bids_layout.get(subject=participant_id, session=session_id, type=image_type,
                                          return_type='file', extensions='nii')
    if len(selected_images) == 0:
        raise RuntimeError('No ' + image_type + ' images were found for participant ' + participant_id
                           + ' and session ' + session_id)
    if len(selected_images) > 1:
        warnings.warn('Several ' + image_type + ' images were found for participant ' + participant_id
                      + ' and session ' + session_id, RuntimeWarning)
    return selected_images[0]

def select_deltaTime(participant_id, bids_directory):
    """
    starting from the tsv with the participant_id, look for the corresponding deltaTime value
    :param participant_id: as found after 'sub-' (ex: ['0040043MACL'])
    :param bids_directory: where to find the 'participants.tsv' file in a path format
    :return: deltaTime, a float corresponding of the time in years between the two MRI (ex: 2.03)
    """
    import pandas as pd
    import os

    # from ['0040043MACL'] to '0040043_MACL'
    participant_id = participant_id[0]
    participant_id = participant_id[0:7] + '_' + participant_id[7:]

    # create a pandas dataframe from 'participants.tsv'
    df = pd.read_csv(os.path.join(bids_directory, 'participants.tsv'), sep="\t")

    # select deltaTime value for participant_id subject
    deltaTime = df.loc[df['participant_id'] == participant_id,'deltaTime'].item()
    return deltaTime

def runSerialLongitudinalRegistration(sesbaseline_image,
                                      seslast_image,
                                      deltaTime,
                                      working_directory,
                                      pipelineFolder,
                                      nameOfNode
                                      ):
    """
    :param sesbaseline_image: (ex: M00_T1w)
    :param seslast_image: (ex: M24_FLAIR)
    :param deltaTime: relative time difference between the first session (sesbaseline) and the last session (seslast)
    :param pipelineFolder: 'path/to/pipeline/folder'
    :return: average nifti image between sesbaseline and seslast
    """
    import sys
    import os
    from nipype.interfaces.matlab import MatlabCommand, get_matlab_command
    from clinica.utils.stream import cprint
    from shutil import copyfile

    working_directory = working_directory + '/t1_volume_longitudinal/serialLongitudinalRegistration_' + nameOfNode \
                        + '/'
    sesbaseline_image = sesbaseline_image[0]
    seslast_image = seslast_image[0]

    # to get the end of the path (name of file) = tail
    (_, sesbaseline_tail) = os.path.split(sesbaseline_image)
    (_, seslast_tail) = os.path.split(seslast_image)

    # copy file to working directory so that it won't work in the 'in' folder
    copyfile(sesbaseline_image, working_directory + sesbaseline_tail)
    sesbaseline_image = working_directory + sesbaseline_tail
    copyfile(seslast_image, working_directory + seslast_tail)
    seslast_image = working_directory + seslast_tail

    # set matlab interface
    MatlabCommand.set_default_matlab_cmd(get_matlab_command())
    matlab = MatlabCommand()
    if sys.platform.startswith('linux'):
        matlab.inputs.args = '-nosoftwareopengl'

    # set input of matlab interface
    matlab.inputs.paths = pipelineFolder
    matlab.inputs.script = """
        serialLongitudinalRegistration('%s', '%s', '%d')
        """ % (sesbaseline_image, seslast_image, deltaTime)
    matlab.inputs.single_comp_thread = False
    matlab.inputs.logfile = os.path.join(working_directory, 'matlab_output.log')
    matlab.inputs.nosplash = True
    matlab.inputs.nodesktop = True

    cprint("******* running Serial Longitudinal Registration matlab script *********")
    matlab.run()

    # get path files that are in working directory to send as output
    avg_oldname = os.path.join(os.path.abspath(working_directory), 'avg_' + sesbaseline_tail)
    avg_newname = avg_oldname.replace('ses-M00_','')
    os.rename(avg_oldname, avg_newname)
    cprint(avg_newname)
    defField_sesbaseline = os.path.join(os.path.abspath(working_directory), 'y_' + sesbaseline_tail)
    defField_seslast = os.path.join(os.path.abspath(working_directory), 'y_' + seslast_tail)

    cprint("******* end of runSerialLongitudinalRegistration *********")
    return avg_newname, defField_sesbaseline, defField_seslast

def runSegmentCAT12(image,
                    matlabToolboxPath,
                    pipelineFolder,
                    working_directory,
                    nameOfNode
                    ):
    """
    :param avg_T1w: ['path/to/image.nii']
    :param sesbaseline_T1w: ['path/to/image.nii']
    :param seslast_T1w: ['path/to/image.nii']
    :param matlabpath: ex: '/Users/emmaducos/Documents/MATLAB'
    :param pipelineFolder: 'path/to/pipeline/folder/'
    :param working_directory: 'path/to/working/directory/'
    :return: c1 and c2 paths for sesbaseline, seslast and avg
    """
    import sys
    import os
    from nipype.interfaces.matlab import MatlabCommand, get_matlab_command
    from clinica.utils.stream import cprint
    from shutil import copyfile

    cprint(image)
    working_directory = working_directory + '/t1_volume_longitudinal/segmentCAT12' + nameOfNode + '/'
    if type(image) == list:
        image = image[0]
    cprint(image)

    # to get the end of the path (name of file) = tail
    (_, tail) = os.path.split(image)

    # copy file to working directory so that it won't work in the 'in' folder
    copyfile(image, working_directory + tail)
    image = working_directory + tail
    cprint(image)

    # the matlab script need a certain format for the paths: 'path/to/file.nii,1'
    image = image + ',1'

    # set matlab interface
    MatlabCommand.set_default_matlab_cmd(get_matlab_command())
    matlab = MatlabCommand()
    if sys.platform.startswith('linux'):
        matlab.inputs.args = '-nosoftwareopengl'

    # set input of matlab interface
    matlab.inputs.paths = pipelineFolder
    matlab.inputs.script = """
    segmentCAT12('%s', '%s')
    """ % (image, matlabToolboxPath)
    matlab.inputs.single_comp_thread = False
    matlab.inputs.logfile = os.path.join(working_directory, 'matlab_output.log')
    matlab.inputs.nosplash = True
    matlab.inputs.nodesktop = True

    cprint("******* running SegmentCAT12 matlab script *********")
    # waiting for the process to finish
    matlab.run()

    # get path files that are in working directory to send as output
    c1 = os.path.join(os.path.abspath(working_directory), 'mri', 'p1' + tail)
    c2 = os.path.join(os.path.abspath(working_directory), 'mri', 'p2' + tail)

    while not os.path.exists(c1):
        pass
    while not os.path.exists(c2):
        pass

    cprint("******* end of runSegmentCAT12 *********")
    return c1, c2

def runLesionSegmentationToolboxLGA(avg_T1w,
                                    avg_FLAIR,
                                    working_directory,
                                    pipelineFolder
                                    ):

    import sys
    import os
    from nipype.interfaces.matlab import MatlabCommand, get_matlab_command
    from clinica.utils.stream import cprint
    from shutil import copyfile

    working_directory = working_directory + '/t1_volume_longitudinal/LSTLGA/'

    # to get the end of the path (name of file) = tail
    (_, avg_T1w_tail) = os.path.split(avg_T1w)
    (_, avg_FLAIR_tail) = os.path.split(avg_FLAIR)

    # copy file to working directory so that it won't work in the 'in' folder
    copyfile(avg_T1w, working_directory + avg_T1w_tail)
    avg_T1w = working_directory + avg_T1w_tail
    copyfile(avg_FLAIR, working_directory + avg_FLAIR_tail)
    avg_FLAIR = working_directory + avg_FLAIR_tail

    # the matlab script need a certain format for the paths: 'path/to/file.nii,1'
    avg_T1w = avg_T1w + ',1'
    avg_FLAIR = avg_FLAIR + ',1'

    # set matlab interface
    MatlabCommand.set_default_matlab_cmd(get_matlab_command())
    matlab = MatlabCommand()
    if sys.platform.startswith('linux'):
        matlab.inputs.args = '-nosoftwareopengl'

    # set input of matlab interface
    matlab.inputs.paths = pipelineFolder
    matlab.inputs.script = """
        lesionSegmentationToolboxLGA('%s', '%s')
        """ % (avg_T1w, avg_FLAIR)
    matlab.inputs.single_comp_thread = False
    matlab.inputs.logfile = os.path.join(working_directory, 'matlab_output.log')
    matlab.inputs.nosplash = True
    matlab.inputs.nodesktop = True

    cprint("******* running LST LGA matlab script *********")
    matlab.run()

    # get path files that are in working directory to send as output
    lesion_map_oldname = os.path.join(os.path.abspath(working_directory),
                                      'ples_lga_0.2_rm' + avg_FLAIR_tail)
    cprint(lesion_map_oldname)
    lesion_map_newname = lesion_map_oldname.replace('ples_lga_0.2_rm', 'lesionMap_')
    lesion_map_newname = lesion_map_newname.replace('_FLAIR', '')
    os.rename(lesion_map_oldname, lesion_map_newname)
    cprint(lesion_map_newname)
    cprint("******* end of runLSTLGA *********")
    return lesion_map_newname

def runImCalc(c1, c2, native_class_images, segmentation_file, lesion_map,
              output,
              expression,
              pipelineFolder, working_directory, nameOfNode
              ):

    import sys
    import os
    from nipype.interfaces.matlab import MatlabCommand, get_matlab_command
    from clinica.utils.stream import cprint
    from clinica.utils.io import unzip_nii
    import time

    working_directory = working_directory + '/t1_volume_longitudinal/imCalc_' + nameOfNode + '/'

    # for c1bin, c2bin, c3bin
    if segmentation_file is None and lesion_map is not None:
        inputFiles = [c1 + ',1', c2 + ',1',
                      native_class_images[0][2][0] + ',1', native_class_images[0][3][0] + ',1',
                      native_class_images[0][4][0] + ',1', native_class_images[0][5][0] + ',1',
                      None, lesion_map + ',1']
    # for c4bin, c5bin, c6bin
    if lesion_map is None and segmentation_file is None and native_class_images is not None:
        inputFiles = [c1 + ',1', c2 + ',1',
                      native_class_images[0][2][0] + ',1', native_class_images[0][3][0] + ',1',
                      native_class_images[0][4][0] + ',1', native_class_images[0][5][0] + ',1',
                      None, None]
    # for c1h
    if c2 is None:
        segmentation_file = unzip_nii(segmentation_file[0])
        inputFiles = [c1 + ',1', None, None, None, None, None,
                      segmentation_file + ',1', None]
    # for c2h
    if native_class_images is None and segmentation_file is None:
        inputFiles = [c1, c2, None, None, None, None, None, None]

    # set matlab interface
    MatlabCommand.set_default_matlab_cmd(get_matlab_command())
    matlab = MatlabCommand()
    if sys.platform.startswith('linux'):
        matlab.inputs.args = '-nosoftwareopengl'

    # set input of matlab interface
    matlab.inputs.paths = pipelineFolder
    matlab.inputs.script = """
            imCalc('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')
            """ % (inputFiles[0], inputFiles[1], inputFiles[2],
                   inputFiles[3], inputFiles[4], inputFiles[5], inputFiles[6], inputFiles[7],
                   output, working_directory, expression)
    matlab.inputs.single_comp_thread = False
    matlab.inputs.logfile = os.path.join(working_directory, 'matlab_output.log')
    matlab.inputs.nosplash = True
    matlab.inputs.nodesktop = True

    cprint("******* running imcalc matlab script *********")
    matlab.run()
    time.sleep(1)

    # get path files that are in working directory to send as output
    binary_mask = os.path.join(os.path.abspath(working_directory), output + '.nii')
    cprint(binary_mask)
    cprint("******* end of imcalc *********")
    return binary_mask

def runDeformationSnmat(snmat, c1h, c2h, c3, avg_T1w, working_directory, pipelineFolder):

    import sys
    import os
    from nipype.interfaces.matlab import MatlabCommand, get_matlab_command
    from clinica.utils.stream import cprint
    from shutil import copyfile

    working_directory = working_directory + '/t1_volume_longitudinal/deformationSnmat/'

    snmat = snmat[0]

    # to get the end of the path (name of file) = tail
    (_, snmat_tail) = os.path.split(snmat)
    (_, c1h_tail) = os.path.split(c1h)
    (_, c2h_tail) = os.path.split(c2h)
    (_, c3_tail) = os.path.split(c3)
    (_, avg_T1w_tail) = os.path.split(avg_T1w)

    # copy file to working directory so that it won't work in the 'in' folder
    copyfile(snmat, working_directory + snmat_tail)
    snmat = working_directory + snmat_tail
    copyfile(c1h, working_directory + c1h_tail)
    c1h = working_directory + c1h_tail
    copyfile(c2h, working_directory + c2h_tail)
    c2h = working_directory + c2h_tail
    copyfile(c3, working_directory + c3_tail)
    c3 = working_directory + c3_tail
    copyfile(avg_T1w, working_directory + avg_T1w_tail)
    avg_T1w = working_directory + avg_T1w_tail


    # set matlab interface
    MatlabCommand.set_default_matlab_cmd(get_matlab_command())
    matlab = MatlabCommand()
    if sys.platform.startswith('linux'):
        matlab.inputs.args = '-nosoftwareopengl'

    # set input of matlab interface
    matlab.inputs.paths = pipelineFolder
    matlab.inputs.script = """
        deformation_snmat('%s', '%s', '%s', '%s', '%s')
        """ % (snmat,
               c1h,
               c2h,
               c3,
               avg_T1w
               )
    matlab.inputs.single_comp_thread = False
    matlab.inputs.logfile = os.path.join(working_directory, 'matlab_output.log')
    matlab.inputs.nosplash = True
    matlab.inputs.nodesktop = True

    cprint("******* running deformation_snmat matlab script *********")
    matlab.run()

    # get path files that are in working directory to send as output
    rdartel_c1h = os.path.join(os.path.abspath(working_directory), 'rdartel_' + c1h_tail)
    rdartel_c2h = os.path.join(os.path.abspath(working_directory), 'rdartel_' + c2h_tail)
    rdartel_c3 = os.path.join(os.path.abspath(working_directory), 'rdartel_' + c3_tail)
    rdartel_avgT1w = os.path.join(os.path.abspath(working_directory), 'rdartel_' + avg_T1w_tail)

    cprint("******* end of deformation_snmat *********")
    return rdartel_c1h, rdartel_c2h, rdartel_c3, rdartel_avgT1w