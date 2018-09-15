multiplot <- function(..., plotlist=NULL, file, cols=1, layout=NULL) {
  library(grid)

  # Make a list from the ... arguments and plotlist
  plots <- c(list(...), plotlist)

  numPlots = length(plots)

  # If layout is NULL, then use 'cols' to determine layout
  if (is.null(layout)) {
    # Make the panel
    # ncol: Number of columns of plots
    # nrow: Number of rows needed, calculated from # of cols
    layout <- matrix(seq(1, cols * ceiling(numPlots/cols)),
                    ncol = cols, nrow = ceiling(numPlots/cols))
  }

 if (numPlots==1) {
    print(plots[[1]])

  } else {
    # Set up the page
    grid.newpage()
    pushViewport(viewport(layout = grid.layout(nrow(layout), ncol(layout))))

    # Make each plot, in the correct location
    for (i in 1:numPlots) {
      # Get the i,j matrix positions of the regions that contain this subplot
      matchidx <- as.data.frame(which(layout == i, arr.ind = TRUE))

      print(plots[[i]], vp = viewport(layout.pos.row = matchidx$row,
                                      layout.pos.col = matchidx$col))
    }
  }
}

 xi=c(24,72); p1=ggplot(data=r, aes(x=i, y=Price)) + scale_y_continuous(labels=function(x) { sprintf('%.0fk', x/1000) }) + geom_point() + theme_bw() + ggtitle('Selling Prices') + geom_vline(xintercept=xi+0.5, color='red'); p2=ggplot(data=r, aes(x=i, y=NumPeople/NumHomes)) + geom_step() + theme_bw() + ggtitle('Demand to Supply Ratio') + geom_hline(yintercept=1, color='red') + geom_vline(xintercept=xi+0.5, color='red') + ylab(''); p3 = ggplot(data=r, aes(x=i, y=NumForSale)) + geom_line() + theme_bw() + geom_vline(xintercept=xi+0.5, color='red') + ggtitle('Liquidity') + ylab('Homes listed for sale'); multiplot(p1, p2, p3)
> xi=c(24,72); p1=ggplot(data=r, aes(x=i, y=Price)) + scale_y_continuous(labels=function(x) { sprintf('%.0fk', x/1000) }) + geom_point() + theme_bw() + ggtitle('Selling Prices') + geom_vline(xintercept=xi+0.5, color='red'); p2=ggplot(data=r, aes(x=i, y=NumPeople/NumHomes)) + geom_step() + theme_bw() + ggtitle('Demand to Supply Ratio') + geom_hline(yintercept=1, color='red') + geom_vline(xintercept=xi+0.5, color='red') + ylab('# Families / # Homes'); p3 = ggplot(data=r, aes(x=i, y=NumForSale)) + geom_line() + theme_bw() + geom_vline(xintercept=xi+0.5, color='red') + ggtitle('Liquidity') + ylab('Homes listed for sale'); multiplot(p1, p2, p3)
