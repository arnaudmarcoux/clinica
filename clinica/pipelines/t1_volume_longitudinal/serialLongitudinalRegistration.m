function serialLongitudinalRegistration(sesbaseline_image, seslast_image, deltaTime)
    % sesbaseline_image, seslast_image format : 'path/to/image'
    % sesbaseline_image : .nii file of baseline
    % seslast_image : .nii file of last measure point
    % deltaTime : time difference in between img0 and img1, in years (eg: 2)

    disp('******running serial longitudinal registration**********')
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

    disp(sesbaseline_image)
    disp(seslast_image)
    % setorigincenter
    % baseline
    for i=1:size(sesbaseline_image,1)
        file = deblank(sesbaseline_image(i,:));
        st.vol = spm_vol(file);
        vs = st.vol.mat\eye(4);
        vs(1:3,4) = (st.vol.dim+1)/2;
        spm_get_space(st.vol.fname,inv(vs));
    end
    % seslast_image
    for i=1:size(seslast_image,1)
        file = deblank(seslast_image(i,:));
        st.vol = spm_vol(file);
        vs = st.vol.mat\eye(4);
        vs(1:3,4) = (st.vol.dim+1)/2;
        spm_get_space(st.vol.fname,inv(vs));
    end

    % the matlab script need a certain format for the paths: 'path/to/file.nii,1'
    centered_sesbaseline_image = strcat(sesbaseline_image, ',1')
    centered_seslast_image = strcat(seslast_image, ',1')
    disp(centered_sesbaseline_image)
    disp(centered_seslast_image)

    matlabbatch{1}.spm.tools.longit.series.vols = {
                                            centered_sesbaseline_image
                                            centered_seslast_image
                                            };
    matlabbatch{1}.spm.tools.longit.series.times = [0 deltaTime]
    matlabbatch{1}.spm.tools.longit.series.noise = NaN;
    matlabbatch{1}.spm.tools.longit.series.wparam = [0 0 100 25 100];
    matlabbatch{1}.spm.tools.longit.series.bparam = 1000000;
    matlabbatch{1}.spm.tools.longit.series.write_avg = 1;
    matlabbatch{1}.spm.tools.longit.series.write_jac = 1;
    matlabbatch{1}.spm.tools.longit.series.write_div = 0;
    matlabbatch{1}.spm.tools.longit.series.write_def = 1;
    
    spm_jobman('run', matlabbatch);
    disp('******serial longitudinal registration done**********')
end
