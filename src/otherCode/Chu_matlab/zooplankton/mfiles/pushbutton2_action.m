function		h=pushbutton2_action(indx)
% pushbutton action
global para status temp

switch indx
    case 1					% Load g and h profile file
        [fname, pathname] =uigetfile('*.mat', 'Load Profile File');
        filename=[pathname fname];
        if isstr(filename)
            temp=load(filename);
        else
            return
        end
        h0_2=findobj('Tag','Fig2');
        hd_segno=findobj(h0_2,'Tag','EditText2SegNo2');
        hd_mean_g=findobj(h0_2,'Tag','EditText2Meang2');
        hd_mean_h=findobj(h0_2,'Tag','EditText2Meanh2');
        hd_std_g=findobj(h0_2,'Tag','EditText2Stdg2');
        hd_std_h=findobj(h0_2,'Tag','EditText2Stdh2');
        hd_corrL=findobj(h0_2,'Tag','EditText2CorrL2');
        set(hd_segno,'string',num2str(temp.seg_no));
        set(hd_corrL,'string',num2str(temp.corrL));
        set(hd_mean_g,'string',sprintf('%7.5g',mean(temp.g)));
        set(hd_std_g,'string',sprintf('%7.5g',std(temp.g)));
        set(hd_mean_h,'string',sprintf('%7.5g',mean(temp.h)));
        set(hd_std_h,'string',sprintf('%7.5g',std(temp.h)));
        hd_segno=findobj(h0_2,'Tag','EditText2SegNo1');
        hd_mean_g=findobj(h0_2,'Tag','EditText2Meang1');
        hd_mean_h=findobj(h0_2,'Tag','EditText2Meanh1');
        hd_std_g=findobj(h0_2,'Tag','EditText2Stdg1');
        hd_std_h=findobj(h0_2,'Tag','EditText2Stdh1');
        hd_corrL=findobj(h0_2,'Tag','EditText2CorrL1');
        set(hd_segno,'string',num2str(temp.seg_no));
        set(hd_corrL,'string',num2str(temp.corrL));
        set(hd_mean_g,'string',sprintf('%7.5g',mean(temp.g)));
        set(hd_std_g,'string',sprintf('%7.5g',std(temp.g)));
        set(hd_mean_h,'string',sprintf('%7.5g',mean(temp.h)));
        set(hd_std_h,'string',sprintf('%7.5g',std(temp.h)));
        subplot(221)
        n_int=length(temp.g);
        hh=plot(1:n_int,temp.g,1:n_int,temp.h,'r');
        xlabel('INDEX ')
        ylabel('Constructed g and h');
        legend(hh,'h','g');
        status.save=1;
    case 2					% Save g and h file
        [fname, pathname] =uiputfile('*.mat', 'Save Profile File');
        filename=[pathname fname];
        if isstr(filename)
            g=temp.g;
            h=temp.h;
            seg_no=temp.seg_no;
            corrL=temp.corrL;
            cmd=['save ''' filename ''' g h seg_no corrL'];
            eval(cmd)
            status.save=1;
        else
            return
        end
    case 3					% Start
        [g,h,Cb,FlucVal]=inhomo_gh;
    case 4					% Save and quit
%         if status.save == 0
%             [fname, pathname] =uiputfile('*.mat', 'Save Profile File');
%             filename=[pathname fname];
%             if isstr(filename)
%                 g=temp.g;
%                 h=temp.h;
%                 seg_no=temp.seg_no;
%                 corrL=temp.corrL;
%                 cmd=['save ' filename ' g h seg_no corrL'];
%                 eval(cmd)
%             else
%                 return
%             end
%         end
        para.phy.g=temp.g;
        para.phy.h=temp.h;
        h0_1=findobj('Tag','Fig1');
        hd_segno=findobj(h0_1,'Tag','EditTextSegment');
        hd_mean_g=findobj(h0_1,'Tag','EditTextg');
        hd_mean_h=findobj(h0_1,'Tag','EditTexth');
        hd_std_g=findobj(h0_1,'Tag','EditTextStdg');
        hd_std_h=findobj(h0_1,'Tag','EditTextStdh');
        hd_corrL=findobj(h0_1,'Tag','EditTextCorrL');
        set(hd_segno,'string',num2str(temp.seg_no));
        set(hd_corrL,'string',num2str(temp.corrL));
        set(hd_mean_g,'string',sprintf('%7.4f',mean(temp.g)));
        set(hd_std_g,'string',sprintf('%7.4f',std(temp.g)));
        set(hd_mean_h,'string',sprintf('%7.4f',mean(temp.h)));
        set(hd_std_h,'string',sprintf('%7.4f',std(temp.h)));
        para.phy.profile=1;
        close
end
