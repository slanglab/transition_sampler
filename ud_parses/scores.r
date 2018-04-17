library(ROCR)
library(dplyr)

# r=lapply(1:7, function(t) {
# 
#     g=readfile(sprintf("edgepred.tlen=%s.greedy",t))
#     g_rec=mean(g$V3[g$V2==1])
#     g_prec=mean(g$V2[g$V3==1])
#     m=readfile(sprintf("edgepred.tlen=%s.mcmap",t))
#     m_rec=mean(m$V3[m$V2==1])
#     m_prec=mean(m$V2[m$V3==1])
#     
#     d=ds[[t]]
#     # d=readfile(sprintf("edgepred.tlen=%s.100sample", t))
#     pp=performance(prediction(d$V2,d$V3),'f')
#     fs = pp@y.values[[1]]
#     fs[!is.finite(fs)] = -1  ## maybe not necessary actually
#     
#     data.frame(t=t,
#                g_rec=g_rec,g_prec=g_prec,
#                m_rec=m_rec,m_prec=m_prec,
#                samplef=max(fs),
#                sample_thresh=pp@x.values[[1]][ which.max(fs) ]
#                )
# }
# )

x=r %>% plyr::ldply(I)
x$gf=with(x, 2*g_prec*g_rec/(g_prec+g_rec))
x$mf=with(x, 2*m_prec*m_rec/(m_prec+m_rec))
options(digits=3)
print(x)

rr=function(value) round(value,3)

# with(x,sprintf("%s & %.3f & %.3f & \\footnotesize{%.3f} \\\\", r(t), r(gf),r(mf), r(samplef), r(sample_thresh))) %>% cat(sep="\n")

cc = gsub("#","", sapply(1:7,getcol))

cat("--------\n\n")
with(x,sprintf("\\textcolor[HTML]{%s}{%s} 
               & \\textcolor[HTML]{%s}{$\\bigcirc$} %.3f 
               & \\textcolor[HTML]{%s}{$\\blacksquare$} 
               %.3f 
               & \\footnotesize{%.2f} 
               & %.3f 
               \\\\", 
               cc, t, 
               cc, rr(gf),
               cc, rr(samplef), (sample_thresh),
               rr(mf)
               )
) %>% gsub(" *\n *"," ",.) %>% cat(sep=" ") 
cat("\n")
