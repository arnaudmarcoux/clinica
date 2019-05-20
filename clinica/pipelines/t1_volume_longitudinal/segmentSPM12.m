function segmentSPM12(avg_T1w, tpm1, tpm2, tpm3, tpm4, tpm5, tpm6)
    % avg_T1w format: '/path/to/image.nii,1'
    % avg_T1w is the average .nii file from the SerialLongitudinalRegistration
    % of two timepoint T1w of one subject (longitudinal study)
    % tpm1 format: '/path/to/TPM.nii,1'
    % tpm2 format: '/path/to/TPM.nii,2' etc.

    % some checks before computing
    disp("****** running segmentSPM12 **********")
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
	matlabbatch{1}.spm.spatial.preproc.channel.vols = {avg_T1w};
    matlabbatch{1}.spm.spatial.preproc.channel.biasreg = 0.001;
    matlabbatch{1}.spm.spatial.preproc.channel.biasfwhm = 60;
    matlabbatch{1}.spm.spatial.preproc.channel.write = [0 0];
    matlabbatch{1}.spm.spatial.preproc.tissue(1).tpm = {tpm1};
    matlabbatch{1}.spm.spatial.preproc.tissue(1).ngaus = 1;
    matlabbatch{1}.spm.spatial.preproc.tissue(1).native = [0 0];
    matlabbatch{1}.spm.spatial.preproc.tissue(1).warped = [0 0];
    matlabbatch{1}.spm.spatial.preproc.tissue(2).tpm = {tpm2};
    matlabbatch{1}.spm.spatial.preproc.tissue(2).ngaus = 1;
    matlabbatch{1}.spm.spatial.preproc.tissue(2).native = [0 0];
    matlabbatch{1}.spm.spatial.preproc.tissue(2).warped = [0 0];
    matlabbatch{1}.spm.spatial.preproc.tissue(3).tpm = {tpm3};
    matlabbatch{1}.spm.spatial.preproc.tissue(3).ngaus = 2;
    matlabbatch{1}.spm.spatial.preproc.tissue(3).native = [1 0];
    matlabbatch{1}.spm.spatial.preproc.tissue(3).warped = [0 0];
    matlabbatch{1}.spm.spatial.preproc.tissue(4).tpm = {tpm4};
    matlabbatch{1}.spm.spatial.preproc.tissue(4).ngaus = 3;
    matlabbatch{1}.spm.spatial.preproc.tissue(4).native = [1 0];
    matlabbatch{1}.spm.spatial.preproc.tissue(4).warped = [0 0];
    matlabbatch{1}.spm.spatial.preproc.tissue(5).tpm = {tpm5};
    matlabbatch{1}.spm.spatial.preproc.tissue(5).ngaus = 4;
    matlabbatch{1}.spm.spatial.preproc.tissue(5).native = [1 0];
    matlabbatch{1}.spm.spatial.preproc.tissue(5).warped = [0 0];
    matlabbatch{1}.spm.spatial.preproc.tissue(6).tpm = {tpm6};
    matlabbatch{1}.spm.spatial.preproc.tissue(6).ngaus = 2;
    matlabbatch{1}.spm.spatial.preproc.tissue(6).native = [1 0];
    matlabbatch{1}.spm.spatial.preproc.tissue(6).warped = [0 0];
    matlabbatch{1}.spm.spatial.preproc.warp.mrf = 1;
    matlabbatch{1}.spm.spatial.preproc.warp.cleanup = 1;
    matlabbatch{1}.spm.spatial.preproc.warp.reg = [0 0.001 0.5 0.05 0.2];
    matlabbatch{1}.spm.spatial.preproc.warp.affreg = 'mni';
    matlabbatch{1}.spm.spatial.preproc.warp.fwhm = 0;
    matlabbatch{1}.spm.spatial.preproc.warp.samp = 3;
    matlabbatch{1}.spm.spatial.preproc.warp.write = [0 0];

    spm_jobman('run', matlabbatch);
    disp("****** segmentSPM12 done **********")
end
