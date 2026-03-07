function       f_out=bscat_ave(x0_in,x_in,f_in,ave_flag,ave_para)
%% INPUTS:
%      x0_in:  output variable on which the output f_in deponds
%      x_in:   simulation variable on which the output f_in depends
%      f_in:   input function
%  ave_flag:   average flag
%              =1,   average over angle
%              =2: average over length
%  ave_para(1) = mean value 
%          (2) = standard deviation
%          (3) = number of variables to be averaged over
%% OUTPUT
%      f_out:  output function

if ave_flag == 1 % average over angle
    [n1,n2]=size(f_in);
    if n1 == 1 | n2 == 1
        ang_std=ave_para(2);
        m1=round(ave_para(3)/2);
        m=2*m1+1;
        n = max(n1,n2);
        for i=1:n
            ang_mean=x_in(i);
            x_ind=find(x_in >= max(ang_mean-3*ang_std, x_in(1)) & x_in <= min(ang_mean+3*ang_std, x_in(end)));
            x_sel=x_in(x_ind);           % selected angle
            f_wgt=pdf('norm',x_sel,ang_mean,ang_std);
            f_out(i)=f_wgt*f_in(x_ind)'/sum(f_wgt);
        end
    else
        ang_mean=ave_para(1);
        ang_std=ave_para(2);
        m1=round(ave_para(3)/2);
        m=2*m1+1;
        x=linspace(ang_mean-3*ang_std,ang_mean+3*ang_std,m);
        wgt=pdf('norm',x,ang_mean,ang_std);
%         if n1 > 1 & n2 > 1
%             n=size(f_in,1);
%         else
%             n=length(f_in);
%         end
        x_ind=find(x_in > ang_mean-3*ang_std & x_in < ang_mean+ 3*ang_std);
        x_sel=x_in(x_ind);           % selected angle
        f_wgt=interp1(x,wgt,x_sel);
%         for i=1:n2
%             f_out(i)=f_wgt*f_in(x_ind,i)/sum(f_wgt);
%         end
        f_out=f_wgt*f_in(x_ind,:)/sum(f_wgt);
    end
elseif ave_flag == 2   % average over length
    len_mean=ave_para(1);
    len_std=ave_para(2);
    if size(f_in,1) > 1 & size(f_in,2) > 1
       x=linspace(len_mean-3*len_std,len_mean+3*len_std,size(f_in,1));
       wgt=pdf('norm',x,len_mean,len_std)';
       n = size(f_in, 2);
       x_sel = x_in(:)/x0_in;
       for i = 1:n
           f_out(i)=sum(f_in(:,i).*wgt.*x_sel.^2)/sum(wgt); 
       end
    else
        m1=round(ave_para(3)/2);
        m=2*m1+1;
        x=linspace(len_mean-3*len_std,len_mean+3*len_std,m);
        wgt=pdf('norm',x,len_mean,len_std)';
        n=length(x_in);
        for i=1:n
            x_ind=find(x_in > x(1)*x0_in(i) & x_in < x(end)*x0_in(i));
            x_sel=x_in(x_ind)/x0_in(i);           % selected ratio
            f_wgt=interp1(x,wgt,x_sel);
            f_out(i)=sum(f_in(x_ind).*f_wgt.*x_sel.^2)/sum(f_wgt);
        end
    end
end

end