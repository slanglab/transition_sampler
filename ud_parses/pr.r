library(ROCR)
library(dplyr)
readfile = function(f) {
    read.table(pipe(sprintf("cat %s | grep EDGEPRED | perl -pe 's/ AAA.*//'", f)))
}
cols = brewer.pal(8,'Dark2')
getcol = function(pathlen) {
    i = pathlen %% 8
    if (i==0) i = 8
    cols[i]
}

# d=read.table(pipe("cat edgepred.100sample | grep EDGEPRED | perl -pe 's/ AAA.*//'"))
# d=readfile("edgepred.100sample")
# pp=performance(prediction(d$V2,d$V3),'prec','rec')
# n=length(pp@y.values[[1]])
# mask=2:(n-1)

# ds = lapply(1:7, function(t) readfile(sprintf("edgepred.tlen=%s.100sample", t)))

pdf("pr.pdf",width=4,height=4.3)

par(family='Times')
plot.new()
plot.window(xaxs='i', yaxs='i', xlim=c(0,1), ylim=c(0,1))
axis(1)
axis(2)
box()
# axis(3,labels=FALSE)
# axis(4,labels=FALSE)
abline(v=seq(0,1,.2),col='gray')
abline(h=seq(0,1,.2),col='gray')
title(xlab="Recall",ylab="Precision")

# legend("top", legend=c("Greedy","Conf \u2265 .9  ", "Conf \u2265 .1"), pch=c(1,24,25),horiz=TRUE, inset=c(0,0))

for (t in 1:7) {
    col = getcol(t)
    d=ds[[t]]
    # d=readfile(sprintf("edgepred.tlen=%s.100sample", t))
    pp=performance(prediction(d$V2,d$V3),'prec','rec')
    n=length(pp@y.values[[1]])
    mask=2:(n-1)
    lines(pp@x.values[[1]][mask], pp@y.values[[1]][mask], col=col)
    g=readfile(sprintf("edgepred.tlen=%s.greedy",t))
    rec=mean(g$V3[g$V2==1])
    prec=mean(g$V2[g$V3==1])
    print(c(prec,rec))
    points(rec,prec, col=col)

# same as 
# > i=which(pp@alpha.values[[1]]==.90)
# > c(pp@x.values[[1]][i], pp@y.values[[1]][i])
    
    prec = function(t) mean(d$V3[d$V2 >= t])
    rec = function(t) mean((d$V2 >= t)[d$V3==1])
    points(rec(.9),prec(.9),pch=24,col=col,cex=.75,bg=col)
    points(rec(.1),prec(.1),pch=25,col=col,cex=.75,bg=col)
    x=pp@x.values[[1]][n-1]
    y=pp@y.values[[1]][n-1]
    # adj = if(t==7) c(2.3,-.3) else c(-.4,-.3)
    adj=c(0.05,-.3)
    text(x,y, sprintf("d=%s",t), adj=adj, col=col, cex=.65)

    pp=performance(prediction(d$V2,d$V3),'f')
    fs = pp@y.values[[1]]
    fs[!is.finite(fs)] = -1  ## maybe not necessary actually
    samplef=max(fs)
    sample_thresh=pp@x.values[[1]][ which.max(fs) ]
    print(c(samplef, rec(sample_thresh), prec(sample_thresh)))
    points(rec(sample_thresh), prec(sample_thresh), col=col, pch=22, bg=col, cex=.7)
    

}

dev.off()
