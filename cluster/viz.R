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