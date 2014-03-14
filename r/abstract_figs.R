require(sqldf)
require(ggplot2)
require(lattice)

load <- function(x) {
	df <- sqldf("select * from results where round=999", dbname=x)
    params <- sqldf("select * from parameters", dbname=x)
    df <- merge(x=df, y=params, by.x="hash", by.y="hash", all.x=TRUE)
    print(sprintf("Loaded %s", x))
    return(df)
}

mush <- function(x, col) {
	#Mush the data to a plottable form
	from <- sprintf(col, 1)
	z <- data.frame(x[from])
	names(z)[names(z)==from] <- "x"
	z$appointment <- 1
	for(i in 2:11) {
		from <- sprintf(col, i)
		c <- data.frame(x[from])
		names(c)[names(c)==from] <- "x"
		c$appointment <- i
		z <- rbind(z, c)
	}
	return(z)
}

honesty_plot <- function(x) {
	col <- "type_2_round_%d_honesty"
	d <- mush(x, col)
	d$x = d$x / x$type_2_pop
	d$group <- "Heavy"
	col <- "type_1_round_%d_honesty"
	e <- mush(x, col)
	e$x = e$x / x$type_1_pop
	e$group <- "Moderate"
	col <- "type_0_round_%d_honesty"
	f <- mush(x, col)
	f$x = f$x / x$type_0_pop
	f$group <- "Light"
	d <- rbind(e, d, f)
	c <- ggplot(d, aes(y=x, x=as.factor(appointment), linetype=group)) + xlab("Appointment") + ylab("Honest signals")
	c <- c + stat_summary(fun.data = "mean_cl_boot", geom="smooth", aes(group=group))   +  theme_bw() + theme(text = element_text(family='CMU Serif',size=15)) + scale_linetype_discrete(name = "Drinking type")
	return(c)
}

honesty_time_plot <- function(x) {
	col <- "type_2_round_%d_honesty"
	d <- mush(x, col)
	d$x = d$x / x$type_2_pop
	d$group <- "Heavy"
	col <- "type_1_round_%d_honesty"
	e <- mush(x, col)
	e$x = e$x / x$type_1_pop
	e$group <- "Moderate"
	d <- rbind(e, d)
	c <- ggplot(d, aes(y=x, x=as.factor(appointment), color=group)) + xlab("Appointment") + ylab("Honest signals")
	c <- c + stat_summary(fun.data = "mean_cl_boot", geom="smooth", aes(group=group))   +  theme_bw() + theme(text = element_text(family='CMU Serif',size=15)) + scale_linetype_discrete(name = "Drinking type")
	return(c)
}

ref_plot <- function(x) {
	col <- "type_2_round_%d_ref"
	d <- mush(x, col)
	d$x = d$x / x$type_2_pop
	d$group <- "Heavy"
	col <- "type_1_round_%d_ref"
	e <- mush(x, col)
	e$x = e$x / x$type_1_pop
	e$group <- "Moderate"
	d <- rbind(e, d)
	col <- "type_0_round_%d_ref"
	e <- mush(x, col)
	e$x = e$x / x$type_0_pop
	e$group <- "Light"
	d <- rbind(e, d)
	c <- ggplot(d, aes(y=x, x=as.factor(appointment), linetype=group)) + xlab("Appointment") + ylab("Referred")
	c <- c + stat_summary(fun.data = "mean_cl_boot", geom="smooth", aes(group=group))   +  theme_bw() + theme(text = element_text(family='CMU Serif',size=15)) + scale_linetype_discrete(name = "Drinking type")
	return(c)
}

file = "/Users/jg1g12/Downloads/jg1g12/%d_abstract_women.db"
print("V0.35")
for(i in 1:10) {
	df <- load(sprintf(file, i))
	dir = "../figures/abstract"
	if(df$women_0 > 0.8) {
    	dir = sprintf("%s/alspac", dir)
    }
    for(i in unique(df$game)) {
            d <- subset(df, df$game == i)
			png(sprintf("%s/honesty_%s_%s.png", dir, as.character(d$game)[1], as.character(d$decision_rule_signaller)[1]))
			print(honesty_plot(d))
			dev.off()

			png(sprintf("%s/ref_%s_%s.png", dir, as.character(d$game)[1], as.character(d$decision_rule_signaller)[1]))
			print(ref_plot(d))
			dev.off()
	}
}