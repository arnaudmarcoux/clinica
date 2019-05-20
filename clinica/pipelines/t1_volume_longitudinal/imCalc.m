function imCalc(c1, c2, c3, c4, c5, c6, segmentation_file, lesion_map, output, outdir, expression)
    % image format: 'path/to/image1,1' 'path/to/image2,1' etc.
    % output format: 'nameOfOutputFile'
    % outdir: 'path/to/output/directory'
    % expression: 'expression' ex: '(((i1>i2).*(i1>i3).*(i1>i4).*(i1>i5).*(i1>i6))-i7)'

    % some checks before computing
    disp("****** running imcalc **********")
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
	if ( strcmp(segmentation_file, 'None') )
	    if ( strcmp(lesion_map, 'None') )
	        if ( strcmp(c3, 'None') )
	            % for c2h
	            matlabbatch{1}.spm.util.imcalc.input = {
	                                                    c1
	                                                    c2
	                                                   };
	        else
	            % for c4bin, c5bin, c6bin
	            matlabbatch{1}.spm.util.imcalc.input = {
	                                                    c1
	                                                    c2
	                                                    c3
	                                                    c4
	                                                    c5
	                                                    c6
	                                                    };
	        end
	    else
	        matlabbatch{1}.spm.util.imcalc.input = {
	                                                c1
	                                                c2
	                                                c3
	                                                c4
	                                                c5
	                                                c6
	                                                lesion_map
	                                                };
	    end
	else
	    matlabbatch{1}.spm.util.imcalc.input = {
	                                            c1
	                                            segmentation_file
	                                            };
    end
    matlabbatch{1}.spm.util.imcalc.output = output;
    matlabbatch{1}.spm.util.imcalc.outdir = {outdir};
    matlabbatch{1}.spm.util.imcalc.expression = expression;
    matlabbatch{1}.spm.util.imcalc.var = struct('name', {}, 'value', {});
    matlabbatch{1}.spm.util.imcalc.options.dmtx = 0;
    matlabbatch{1}.spm.util.imcalc.options.mask = 0;
    matlabbatch{1}.spm.util.imcalc.options.interp = 1;
    matlabbatch{1}.spm.util.imcalc.options.dtype = 4;

	spm_jobman('run', matlabbatch);
    disp("****** imcalc done **********")
end
