library(ggplot2)

YDS_histogram <- function(climb){
  # filter to only routes
  climb = climb[climb$rateYDS != '',]
  
  # most climbs are between 5.5 and 5.14
  grade_breaks = seq(5, 14.5, by = 0.5)
  # magic number math to make pretty labels
  grd = rep(4:13, each = 2)
  adj = rep(c('','+'), 10)
  grade_labels = paste0('5.',grd, adj)
  names(grade_breaks) = grade_labels
  
  # compare YDS rate to pretty grades and return name of closest one
  climb$clean_label = unlist(lapply(
    climb$rateFloatYDS, function(g) {
      grade_labels[which.min(abs(grade_breaks - g))]
    }
  ))
  
  # count how many climbs fall into each grade
  grade_histo = sqldf("
                      select
                      clean_label,
                      count(distinct href) num_climbs,
                      avg(rateFloatYDS) hard
                      from climb
                      group by clean_label
                      order by hard
                      ")
  # classic reorder for bar plot
  grade_histo$clean_label = reorder(grade_histo$clean_label, grade_histo$hard)
  
  # plot count frequency versus difficulty
  plt = ggplot(data=grade_histo)
  plt = plt + geom_bar(stat='identity', aes(x = clean_label, y = num_climbs))
  plt = plt + labs(title="Climbs are Most Often 5.10")
  plt = plt + labs(x="Difficulty", y="Number of Climbs")
  
  return(plt)
}

Hueco_histogram <- function(climb){
  # filter to only routes
  climb = climb[climb$rateHueco != '',]
  
  # most climbs are between 5.5 and 5.14
  grade_breaks = seq(1, 16, by=1)
  # magic number math to make pretty labels
  grd = rep(0:15, each=1)
  grade_labels = paste0('V',grd)
  names(grade_breaks) = grade_labels
  
  # compare YDS rate to pretty grades and return name of closest one
  climb$clean_label = unlist(lapply(
    climb$rateFloatHueco, function(g) {
      grade_labels[which.min(abs(grade_breaks - g))]
    }
  ))
  
  # count how many climbs fall into each grade
  grade_histo = sqldf("
                      select
                      clean_label,
                      count(distinct href) num_climbs,
                      avg(rateFloatHueco) hard
                      from climb
                      group by clean_label
                      order by hard
                      ")
  # classic reorder for bar plot
  grade_histo$clean_label = reorder(grade_histo$clean_label, grade_histo$hard)
  
  # plot count frequency versus difficulty
  plt = ggplot(data=grade_histo)
  plt = plt + geom_bar(stat='identity', aes(x = clean_label, y = num_climbs))
  plt = plt + labs(title="Climbs are Most Often V6")
  plt = plt + labs(x="Difficulty", y="Number of Climbs")
  
  return(plt)
}

trend_scatter <- function(climb, x_string, y_string, limits = c(), log_scale = FALSE) {
  # consider marginal plots here??
  vote_thresh = 3
  
  # throw out NA records
  climb = climb[!is.na(climb$max_type),]
  
  # jitter heaped values
  climb[[y_string]] = jitter(climb[[y_string]])
  climb[[x_string]] = jitter(climb[[x_string]])
  
  # filter to reasonable lengths
  if(length(limits) > 0) {
    within_limits = climb[[x_string]]>limits[1] & climb[[x_string]]<limits[2]
    climb = climb[within_limits,]
  }
  
  # only consider respectable vote counts
  climb = climb[climb$starvotes>vote_thresh,]
  
  # plot
  plt = ggplot(data=climb, aes_string(
    x = x_string, y = y_string,
    colour = 'max_type'
    ), size = 1)
  plt = plt + geom_point(alpha = 0.5)
  # guide legend = 'None'
  # log scale if you're into that
  if(log_scale) { plt = plt + scale_x_log10() }
  # add trend lines
  plt = plt + stat_smooth(method = 'lm', se = FALSE)
  
  # title and axes labels
  plt = plt + labs(title="Taller Climbs Tend to Be Rated Higher")
  plt = plt + labs(x=x_string, y=y_string)
  
  return(plt)
}
