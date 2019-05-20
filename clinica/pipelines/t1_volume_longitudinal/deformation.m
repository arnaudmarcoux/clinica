function deformation(composition_importedSnMat_ParameterFile, composition_importedSnMat_voxelSizes, composition_inverse_composition_deformationField, composition_inverse_imageToBaseInverseOn, composition_deformationField_1, composition_deformationField_2, output_pullback_applyTo_c1h, output_pullback_applyTo_c2h, output_pullback_applyTo_c3, output_pullback_applyTo_avgT1w, output_pullback_interpolation, output_pullback_filenamePrefix, output_saveDeformation_saveAs, output_pushforward_applyTo, output_pushforward_fieldOfView_imageDefined, output_pushforward_filenamePrefix)

    % some checks before computing
    disp("****** running LesionSegmentationToolboxLGA **********")
    warning on all
    warning off backtrace
    warning on verbose
    if isempty(which('spm'))
        throw(MException('SPMCheck:NotFound', 'SPM not in matlab path'));
    end
    [name, version] = spm('ver');
    fprintf('SPM version: %s Release: %s\n',name, version);
    fprintf('SPM path: %s\n', which('spm'));
    spm('Defaults','PET');
    if strcmp(name, 'SPM8') || strcmp(name(1:5), 'SPM12')
        spm_jobman('initcfg');
        spm_get_defaults('cmdline', 1);
    end

    % the actual computing work, extracted from a *_job.m file from the batch utilitary of SPM12

    if (strcmp(composition_importedSnMat_ParameterFile, 'None') == 0)
        % composition: new imported _sn.mat
        matlabbatch{1}.spm.util.defs.comp{1}.sn2def.matname = composition_importedSnMat_ParameterFile;
        matlabbatch{1}.spm.util.defs.comp{1}.sn2def.vox = [1 1 1]; % value chosen by N. Villain
        matlabbatch{1}.spm.util.defs.comp{1}.sn2def.bb = [NaN NaN NaN
                                                        NaN NaN NaN];

    elseif (strcmp(composition_inverse_composition_deformationField, 'None') == 0)
        % composition: new inverse
        matlabbatch{1}.spm.util.defs.comp{1}.inv.comp{1}.def = composition_inverse_composition_deformationField;
        matlabbatch{1}.spm.util.defs.comp{1}.inv.space = composition_inverse_imageToBaseInverseOn;

    elseif (strcmp(composition_deformationField_1, 'None') == 0)
        % composition: new deformation field
        matlabbatch{1}.spm.util.defs.comp{1}.def = composition_deformationField_1;

    elseif (strcmp(composition_deformationField_2, 'None') == 0)
        % composition: new deformation field
        matlabbatch{1}.spm.util.defs.comp{1}.def = composition_deformationField_2;

    elseif (strcmp(output_pullback_applyTo, 'None') == 0)
        % output: new pullback
        matlabbatch{1}.spm.util.defs.out{1}.pull.fnames = {output_pullback_applyTo_c1h
                                                           output_pullback_applyTo_c2h
                                                           output_pullback_applyTo_c3
                                                           output_pullback_applyTo_avgT1w};
        matlabbatch{1}.spm.util.defs.out{1}.pull.savedir.savesrc = 1; % output destination = source directory
        matlabbatch{1}.spm.util.defs.out{1}.pull.interp = output_pullback_interpolation; % NN = 0 ; 4th = 4
        matlabbatch{1}.spm.util.defs.out{1}.pull.mask = 1;
        matlabbatch{1}.spm.util.defs.out{1}.pull.fwhm = [0 0 0];
        matlabbatch{1}.spm.util.defs.out{1}.pull.prefix = output_pullback_filenamePrefix;

    elseif (strcmp(output_saveDeformation_saveAs, 'None') == 0)
        % output: save deformation field
        matlabbatch{1}.spm.util.defs.out{1}.savedef.ofname = output_saveDeformation_saveAs;
        matlabbatch{1}.spm.util.defs.out{1}.savedef.savedir.savesrc = 1;

    elseif (strcmp(output_pushforward_applyTo, 'None') == 0)
        % output : new pushforward
        matlabbatch{1}.spm.util.defs.out{1}.push.fnames = output_pushforward_applyTo;
        matlabbatch{1}.spm.util.defs.out{1}.push.weight = {''};
        matlabbatch{1}.spm.util.defs.out{1}.push.savedir.savesrc = 1;
        matlabbatch{1}.spm.util.defs.out{1}.push.fov.file = output_pushforward_fieldOfView_imageDefined;
        matlabbatch{1}.spm.util.defs.out{1}.push.preserve = 0;
        matlabbatch{1}.spm.util.defs.out{1}.push.fwhm = [0 0 0];
        matlabbatch{1}.spm.util.defs.out{1}.push.prefix = output_pushforward_filenamePrefix;
    end

    % run
    spm_jobman('run', matlabbatch);
    disp('****** LesionSegmentationToolboxLGA done **********')
end
