bucket_for_calib = function(pred, bucket_size=10000) {

# use the dynamic algorithm in nguyen 2015
# ties make this hard. nearly half of edges have pred prob .01 and can't put
# into multiple buckets.  not clear to me what the R builtins ecdf/rank/cut
# do in this situation, so just writing it procedurally to make sure i get
# what i want.

    # rpred = rank(pred)
    # pred_counts = table(rpred)
    pred_counts = table(pred)
# 'i' is index of original space buckets.
# now need to group into final buckets
# need to do this iteratively, which is awkward for R but oh well
    ind2bucket = rep(0, length(pred_counts))
    bucket_counts = rep(0, length(pred_counts)) ## longer than necessary
    cur_bucket = 1
    for (i in 1:length(pred_counts)) {
        if (bucket_counts[cur_bucket] >= bucket_size) {
            cur_bucket = cur_bucket + 1
        }
        ind2bucket[i] = cur_bucket
        bucket_counts[cur_bucket] = bucket_counts[cur_bucket] + pred_counts[i]
    }
    num_buckets = max(ind2bucket)
    stopifnot(num_buckets == ind2bucket[length(ind2bucket)])
    stopifnot(all(ind2bucket >= 1))
    bucket_counts = bucket_counts[bucket_counts > 0]
# UGH have to rely on string encoding of predictions.
# match() seems to do it correctly.
    preds_as_orig_buckets = match(pred, names(pred_counts))
    preds_as_coarser_buckets = ind2bucket[preds_as_orig_buckets]

    bucket_min = sapply(1:num_buckets, function(b) min(as.numeric(names(pred_counts)[ ind2bucket==b ])))
    bucket_max = sapply(1:num_buckets, function(b) max(as.numeric(names(pred_counts)[ ind2bucket==b ])))
    list(pred=pred, ind2bucket=ind2bucket, num_buckets=num_buckets, bucket_counts=bucket_counts, bucketed_pred=preds_as_coarser_buckets, bucket_min=bucket_min,bucket_max=bucket_max)
}

calc_calib_buckets = function(d) {
    mask1 = d$V2 > 0
    pred = d$V2[mask1]
    gold = d$V3[mask1]
    x = bucket_for_calib(pred, bucket_size=5000)
    print(x$bucket_counts)
    z=plyr::ldply(1:x$num_buckets, function(b) { 
            mask2 = x$bucketed_pred==b
            # print(table(mask2))
            # print(pred[mask2])
            data.frame(pred=mean(pred[mask2]), empir=mean(gold[mask2]))
        })
    z$bucket_min=x$bucket_min
    z$bucket_max=x$bucket_max
    z$bucket_count=x$bucket_count
    list(x=x,z=z)
}    

add_calib_line = function(d,col='black') {
    z = calc_calib_buckets(d)$z
    # print(z)
    points(z$pred, z$empir, col=col)
    lines(z$pred, z$empir, col=col)
    # x
}

calib_rmse = function(d) {
    r = calc_calib_buckets(d)
    # w = r$x$bucket_counts * r$z$pred  ## you need this for E_q[ (q-p)^2 ] ??
    w = r$x$bucket_counts ## this is in nguyen 2015 - might be wrong actually.
    mse = weighted.mean((r$z$empir - r$z$pred)^2, w)
    sqrt(mse)
    # as.vector(sqrt(r$x$bucket_counts %*% (r$z$empir-r$z$pred)**2 / sum(r$x$bucket_counts)))
    # as.vector(sqrt(r$x$bucket_counts %*% (r$z$empir-r$z$pred)**2 / sum(r$x$bucket_counts)))
}

pdf("calib.pdf",width=4,height=4.3)
par(family='Times')

plot.new()
# plot.window(xlim=c(0,1),ylim=c(0,1),xaxs='i',yaxs='i')
plot.window(xlim=c(0,1),ylim=c(0,1))
axis(1)
axis(2)
box()
abline(v=seq(0,1,.2),col='gray')
abline(h=seq(0,1,.2),col='gray')
abline(a=0,b=1)
title(xlab="Predicted prob.", ylab="Empirical gold-standard prob.")
lens=c(1,2,3,7)
legend("topleft", legend=sprintf("length %s",lens), fill=cols[lens], text.col=cols[lens], border=cols[lens], bg='white', cex=.8)

for (t in lens) {
    col = getcol(t)
    # d=readfile(sprintf("edgepred.tlen=%s.100sample", t))
    d=ds[[t]]
    add_calib_line(d, col=getcol(t))
}

dev.off()
