function deformation_snmat(snmat, c1h, c2h, c3, avg_T1w)
    % snmat format: '/path/to/*_seg_sn.mat'
    % avg_T1w is the average .nii file from the SerialLongitudinalRegistration
    % of two timepoint T1w of one subject (longitudinal study)
    % idem avg_FLAIR

    % some checks before computing
    disp("****** running deformation_snmat **********")
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
	matlabbatch{1}.spm.util.defs.comp{1}.sn2def.matname = {snmat};
    matlabbatch{1}.spm.util.defs.comp{1}.sn2def.vox = [1 1 1]; % decided by nicolas
    matlabbatch{1}.spm.util.defs.comp{1}.sn2def.bb = [NaN NaN NaN
                                                      NaN NaN NaN];
    matlabbatch{1}.spm.util.defs.out{1}.pull.fnames = {
                                                    c1h
                                                    c2h
                                                    c3
                                                    avg_T1w
                                                     };
    matlabbatch{1}.spm.util.defs.out{1}.pull.savedir.savepwd = 1;
    matlabbatch{1}.spm.util.defs.out{1}.pull.interp = 4;
    matlabbatch{1}.spm.util.defs.out{1}.pull.mask = 1;
    matlabbatch{1}.spm.util.defs.out{1}.pull.fwhm = [0 0 0];
    matlabbatch{1}.spm.util.defs.out{1}.pull.prefix = 'rdartel_';

    spm_jobman('run', matlabbatch);
    disp("****** deformation_snmat done **********")
end
