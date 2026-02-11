function		h=pushbutton_action(indx);
% pushbutton action
global para status dat

switch indx
  case 0					% load shape profile file
    [fname, pathname] =uigetfile('*.dat', 'Load Shape Profile File');
    filename=[pathname fname];
    if isstr(filename)
      para.shape.prof_name=filename; 
    else
      return
    end
  case 1					% Load configuration file
    [fname, pathname] =uigetfile('*.dat', 'Load Configuartion File');
    filename=[pathname fname];
    if isstr(filename)
      h=load_parameters(filename); 
      h=set_parameters;
    else
      return
    end
  case 2					% Save configuration file
    [fname, pathname] =uiputfile('*.dat', 'Save Configuartion File');
    filename=[pathname fname];
    if isstr(filename)  
       h=get_parameters;  
       h=save_parameters(filename); 
    else
      return
    end
  case 3					% Save outputs to file
    [fname, pathname] =uiputfile('*.mat', 'Save Outputs to File');
    filename=[pathname fname];
    if isstr(filename)
        cmd=['save ''' filename ''' para  dat'];
        eval(cmd)
    end
  case 4					% Start Computation
    h=get_parameters;  
    h=bscat;
  case 5					% Stop
    status.stop=1;
   disp(sprintf('stop = %g',status.stop))
end