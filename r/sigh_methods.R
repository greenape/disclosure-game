require(sqldf)
require(ggplot2)

num_rounds_type <- function(dataset, type, x, y) {
    s = eval(parse(text=sprintf("subset(dataset, dataset$type_%d_finished > 0)", type)))
    #dataset <- subset(dataset, filter > 0)
    # Average number of rounds played
    #x = eval(parse(text=sprintf("dataset$%s",x)))
    #y = eval(parse(text=sprintf("dataset$%s",y)))
    fill = sprintf("rounds_played_type_%d", type)
    z = data.frame(s[c(x,y,fill)])
    names(z)[names(z)==x] <- "x"
    names(z)[names(z)==y] <- "y"
    names(z)[names(z)==fill] <- "fill"
    z <- aggregate(z, by=list(z$x, z$y), FUN=mean)
    c <- ggplot(z, aes(x=x, y=y, z=fill, fill=fill))
    return(c + geom_tile())
}

rounds_dist <- function(dataset, x, y) {
    #s = eval(parse(text=sprintf("subset(dataset, dataset$type_%d_finished > 0)", type)))
    #dataset <- subset(dataset, filter > 0)
    # Average number of rounds played
    #x = eval(parse(text=sprintf("dataset$%s",x)))
    #y = eval(parse(text=sprintf("dataset$%s",y)))
    #fill = sprintf("rounds_played_type_%d", type)
    a = (12 - df$rounds_played_type_0)^2
    b = (1 - df$rounds_played_type_1)^2
    c = (1 - df$rounds_played_type_2)^2
    za = data.frame(dataset[c(x,y)])
    za$fill = a#scale(a, center = FALSE)
    zb = data.frame(dataset[c(x,y)])
    zb$fill = b#scale(b, center = FALSE)
    zc = data.frame(dataset[c(x,y)])
    zc$fill = c#scale(c, center = FALSE)
    z = rbind(za, zb, zc)
    z$fill = scale(z$fill, center = FALSE)

    names(z)[names(z)==x] <- "x"
    names(z)[names(z)==y] <- "y"
    #names(z)[names(z)==fill] <- "fill"
    z <- aggregate(z, by=list(z$x, z$y), FUN=mean)
    c <- ggplot(z, aes(x=x, y=y, z=fill, fill=fill))
    return(c + geom_tile())
}

rounds_diff <- function(dataset, x, y) {
    #s = eval(parse(text=sprintf("subset(dataset, dataset$type_%d_finished > 0)", type)))
    #dataset <- subset(dataset, filter > 0)
    # Average number of rounds played
    #x = eval(parse(text=sprintf("dataset$%s",x)))
    #y = eval(parse(text=sprintf("dataset$%s",y)))
    #fill = sprintf("rounds_played_type_%d", type)
    a = df$rounds_played_type_0_upto
    b = (a - df$rounds_played_type_1_upto)
    c = (a - df$rounds_played_type_2_upto)
    #za = data.frame(dataset[c(x,y)])
    #za$fill = a#scale(a, center = FALSE)
    zb = data.frame(dataset[c(x,y)])
    zb$fill = b#scale(b, center = FALSE)
    zc = data.frame(dataset[c(x,y)])
    zc$fill = c#scale(c, center = FALSE)
    z = rbind(zb, zc)

    names(z)[names(z)==x] <- "x"
    names(z)[names(z)==y] <- "y"
    #names(z)[names(z)==fill] <- "fill"
    z <- aggregate(z, by=list(z$x, z$y), FUN=mean)
    #z$fill = scale(z$fill, center = FALSE)
    c <- ggplot(z, aes(x=x, y=y, z=fill, fill=fill))
    return(c + geom_tile())
}

payoffs_type <- function(dataset, type, x, y) {
    # Average payoff accrued
    s = eval(parse(text=sprintf("subset(dataset, dataset$type_%d_finished > 0)", type)))
    #dataset <- subset(dataset, filter > 0)
    fill = sprintf("accrued_payoffs_type_%d", type)
    z = data.frame(s[c(x,y,fill)])
    names(z)[names(z)==x] <- "x"
    names(z)[names(z)==y] <- "y"
    names(z)[names(z)==fill] <- "fill"
    #fill = eval(parse(text=sprintf("dataset$accrued_payoffs_type_%d", type)))
    z <- aggregate(z, by=list(z$x, z$y), FUN=mean)
    c <- ggplot(z, aes(x=x, y=y, z=fill, fill=fill))
    return(c + geom_tile())
}

signals_type <- function(dataset, type, signal, x, y) {
    # Levelplot of average signal frequency across whole game
    # Include only rounds where at least some of that type played
    # Type 0
    #s = eval(parse(text=sprintf("subset(dataset, dataset$type_%d_frequency > 0)", type)))
    s <- dataset
    #dataset <- subset(dataset, filter > 0)
    # Average payoff accrued
    fill = sprintf("type_%d_signal_%d", type, signal)
    z = data.frame(s[c(x,y,fill)])
    names(z)[names(z)==x] <- "x"
    names(z)[names(z)==y] <- "y"
    names(z)[names(z)==fill] <- "fill"
    #fill = eval(parse(text=sprintf("dataset$type_%d_signal_%d", type, signal)))
    z <- aggregate(z, by=list(z$x, z$y), FUN=mean)
    c <- ggplot(z, aes(x=x, y=y, z=fill, fill=fill))
    return(c + geom_tile())
}

honesty_type <- function(dataset, type, x, y) {
    # Levelplot of normalised average absolute signal distance.
    # Include only rounds where at least some of that type played
    # Type 0
    dataset = eval(parse(text=sprintf("subset(dataset, dataset$type_%d_frequency > 0)", type)))
    #dataset <- subset(dataset, filter > 0)
    # Average payoff accrued
    x = eval(parse(text=sprintf("dataset$%s",x)))
    y = eval(parse(text=sprintf("dataset$%s",y)))
    for(signal in 0:2) {
         fill = eval(parse(text=sprintf("dataset$type_%d_signal_%d", type, signal)))
    }
    #dataset <- aggregate(dataset, by=list(x, y), FUN=mean)
    c <- ggplot(dataset, aes(x=x, y=y))
    return(c + geom_tile(aes(fill=fill)))
}


load <- function(x) {
    dataset <- sqldataset("select * from results", dbname=x)
    params <- sqldataset("select * from parameters", dbname=x)
    dataset <- merge(x=dataset, y=params, by.x="hash", by.y="hash", all.x=TRUE)
    print(sprintf("Loaded %s", x))
    return(dataset)
}

num_rounds <- function(dataset) {
    # Average number of rounds played over time for all types
    # Include only rounds where at least some of that type finished
    # Type 0
    s <- subset(dataset, dataset$type_0_finished > 0)
    d <- data.frame(s[c('appointment','rounds_played_type_0')])
    names(d)[names(d)=="rounds_played_type_0"] <- "num_rounds"
    d$player_type <- "Light"
    print("Light.")
    # Type 1
    s <- subset(dataset, dataset$type_1_finished > 0)
    e <- data.frame(s[c('appointment', 'rounds_played_type_1')])
    e$player_type <- "Moderate"
    names(e)[names(e)=="rounds_played_type_1"] <- "num_rounds"
    d <- rbind(d, e)
    print("Mod.")
    rm(e)
    # Type 2
    s <- subset(dataset, dataset$type_2_finished > 0)
    e <- data.frame(s[c('appointment', 'rounds_played_type_2')])
    e$player_type <- "Heavy"
    names(e)[names(e)=="rounds_played_type_2"] <- "num_rounds"
    d <- rbind(d, e)
    print("High.")
    
    c <- ggplot(d, aes(x=appointment, y=num_rounds, color=player_type)) + xlab("Appointment") + ylab("Rounds played")
    c <- c + stat_summary(fun.data = "mean_cl_boot", geom="smooth", aes(group=player_type))   +  theme(text = element_text(family='CMU Serif',size=15)) + scale_colour_discrete(name = "Type")
    return(c)
}

signals_by_type <- function(dataset, type) {
    # Include only rounds where at least some of that type played
    # Type 0
    dataset = eval(parse(text=sprintf("subset(dataset, dataset$type_%d_frequency > 0)", type)))
    #dataset <- subset(dataset, filter > 0)
    data = "type_%d_signal_%d"
    a = sprintf(data, type, 0)
    b = sprintf(data, type, 1)
    c = sprintf(data, type, 2)
    d <- data.frame(s[c('appointment', a)])
    d$signal <- "Light"
    names(d)[names(d)==a] <- "frequency"
    # Type 1
    e <- data.frame(s[c('appointment', b)])
    e$signal <- "Moderate"
    names(e)[names(e)==b] <- "frequency"
    d <- rbind(d, e)
    # Type 2
    e <- data.frame(s[c('appointment', c)])
    e$signal <- "Heavy"
    names(e)[names(e)==c] <- "frequency"
    d <- rbind(d, e)
    
    c <- ggplot(d, aes(x=appointment, y=frequency, color=signal)) + xlab("Appointment") + ylab("Signal frequency")
    c <- c + stat_summary(fun.data = "mean_cl_boot", geom="smooth", aes(group=signal))   +  theme(text = element_text(family='CMU Serif',size=15)) + scale_colour_discrete(name = "Signal")
    return(c)
}

load <- function(x, appointment=999) {
    query = sprintf("select * from results where appointment=%d", appointment)
    dataset <- sqldf(query, dbname=x)
    params <- sqldf("select * from parameters", dbname=x)
    dataset <- merge(x=dataset, y=params, by.x="hash", by.y="hash", all.x=TRUE)
    print(sprintf("Loaded %s", x))
    return(dataset)
}