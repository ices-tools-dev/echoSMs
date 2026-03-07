%% smoothing with moving average filter of length n
%function y=smooth(yi,n)
function y=smooth(yi,n)

if n <= 1
 y=yi;
 return
end
y=yi;
nl=length(yi);
if n > nl
  n=nl;
end
m=floor(n/2);
for i=1:m
  y(i)=mean_nan(yi(max(1,i-m):i+m));
end
for i=m+1:nl-m
  y(i)=mean_nan(yi(i-m:i+m));
end
for i=nl-m+1:nl
  y(i)=mean_nan(yi(i-m:min(i+m,nl)));
end
