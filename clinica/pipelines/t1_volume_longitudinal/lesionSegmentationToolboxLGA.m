function lesionSegmentationToolboxLGA(avg_T1w, avg_FLAIR)
    % avg_T1w format: 'path/to/image,1'
    % avg_T1w is the average .nii file from the SerialLongitudinalRegistration
    % of two timepoint T1w of one subject (longitudinal study)
    % idem avg_FLAIR

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
	matlabbatch{1}.spm.tools.LST.lga.data_T1 = {avg_T1w};
	matlabbatch{1}.spm.tools.LST.lga.data_F2 = {avg_FLAIR};
	matlabbatch{1}.spm.tools.LST.lga.opts_lga.initial = 0.2;
	matlabbatch{1}.spm.tools.LST.lga.opts_lga.mrf = 0.5;
	matlabbatch{1}.spm.tools.LST.lga.opts_lga.maxiter = 50;
	matlabbatch{1}.spm.tools.LST.lga.html_report = 1;
	
    spm_jobman('run', matlabbatch);
    disp("****** LesionSegmentationToolboxLGA done **********")
end
