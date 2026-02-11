function		h=radio_action(indx);
% radiobutton action

h1=findobj(gcf,'Tag','RadiobuttonUniPDF');
h2=findobj(gcf,'Tag','RadiobuttonGaussPDF');
switch indx
	case 1				% Uniform PDF
    set(h1,'value',1);
    if  get(h1,'Value') == 1
       set(h2,'value',0);
       h3=findobj(gcf,'Tag','StaticTextStdTheta');
       set(h3,'String','Half range of theta');
     end
	case 2				% Gaussian PDF
     set(h2,'value',1);
     if  get(h2,'Value') == 1
       set(h1,'value',0);
       h3=findobj(gcf,'Tag','StaticTextStdTheta');
       set(h3,'String','Std of theta');
     end
end