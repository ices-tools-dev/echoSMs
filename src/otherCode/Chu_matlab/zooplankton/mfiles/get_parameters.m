%% get parameters from the configuration panel and pass to the structure: para
function				h=get_parameters;
global 	para	

% home directory
if isempty(para) | isempty(para.info.home_dir)
  para.info.home_dir=pwd;
end

%get shape parameters
h=findobj(gcf,'Tag','EditTextLength');
para.shape.L=str2num(get(h,'String'));
h=findobj(gcf,'Tag','EditTextRho_L');
para.shape.rho_L=str2num(get(h,'String'));
h=findobj(gcf,'Tag','EditTextL_a');
para.shape.L_a=str2num(get(h,'String'));
h=findobj(gcf,'Tag','EditTextTaperOrder');
para.shape.order=str2num(get(h,'String'));
h=findobj(gcf,'Tag','CheckboxLengthAve');
para.shape.ave_flag=get(h,'Value');
h=findobj(gcf,'Tag','EditTextStdL');
para.shape.Lstd=str2num(get(h,'String'));
h=findobj(gcf,'Tag','EditTextDL');
para.shape.dL=str2num(get(h,'String'));
h=findobj(gcf,'Tag','CheckboxProfile');
if get(h,'Value') == 1
  if isempty(para.shape.prof_name) | strcmp('-1',para.shape.prof_name) == 1
    [fname, pathname] =uigetfile('*.dat', 'Select A Shape Profile File');
    filename=[pathname fname];
    if isstr(filename)
      para.shape.prof_name=filename; 
    else
      return
    end
  end
else
   para.shape.prof_name='-1';
end 
h=findobj(gcf,'Tag','EditTextAxisSmooth');
para.shape.axis_sm=str2num(get(h,'String'));
h=findobj(gcf,'Tag','EditTextTaperSmooth');
para.shape.taper_sm=str2num(get(h,'String'));
% disp('**** get_parameters! ****')

% get orientation parameters
h=findobj(gcf,'Tag','EditTextMeanTheta');
para.orient.angm=str2num(get(h,'String'));
h=findobj(gcf,'Tag','EditTextTheta0');
para.orient.ang0=str2num(get(h,'String'));
h=findobj(gcf,'Tag','EditTextTheta1');
para.orient.ang1=str2num(get(h,'String'));
h=findobj(gcf,'Tag','CheckboxOrientAve');
para.orient.ave_flag=get(h,'Value');
h=findobj(gcf,'Tag','RadiobuttonUniPDF');
if get(h,'Value') == 1
   para.orient.PDF=1;
else
   para.orient.PDF=2;
end
h=findobj(gcf,'Tag','EditTextStdTheta');
para.orient.PDF_para=str2num(get(h,'String'));
h=findobj(gcf,'Tag','EditTextDtheta');
para.orient.dang=str2num(get(h,'String'));

% get physical property parameters
h=findobj(gcf,'Tag','EditTextg');
para.phy.g0=str2num(get(h,'String'));
h=findobj(gcf,'Tag','EditTexth');
para.phy.h0=str2num(get(h,'String'));
h=findobj(gcf,'Tag','EditTextSegment');
para.phy.seg_no=str2num(get(h,'String'));
h=findobj(gcf,'Tag','EditTextStdg');
para.phy.g_std=str2num(get(h,'String'));
h=findobj(gcf,'Tag','EditTextStdh');
para.phy.h_std=str2num(get(h,'String'));
h=findobj(gcf,'Tag','EditTextCorrL');
para.phy.corrL=str2num(get(h,'String'));

% get simulation parameters
h=findobj(gcf,'Tag','PopupMenuOutput');
para.simu.out_indx=get(h,'Value');
h=findobj(gcf,'Tag','PopupMenuVar');
para.simu.var_indx=get(h,'Value');
h=findobj(gcf,'Tag','EditTextNint');
para.simu.ni=str2num(get(h,'String'));
h=findobj(gcf,'Tag','EditTextNpts');
para.simu.n=str2num(get(h,'String'));
h=findobj(gcf,'Tag','EditTextVar0');
para.simu.var0=str2num(get(h,'String'));
h=findobj(gcf,'Tag','EditTextVar1');
para.simu.var1=str2num(get(h,'String'));
h=findobj(gcf,'Tag','EditTextFreq');
para.simu.freq=str2num(get(h,'String'));
h=0;