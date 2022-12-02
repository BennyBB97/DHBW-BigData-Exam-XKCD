<?php

if(isset($_GET['search'])){
    $sqlhost = "172.18.0.4";
    $sqluser = "xkcd";
    $sqlpass = "4dmin";
    $dbname  = "bigdata";

    $my_db = mysqli_connect($sqlhost, $sqluser, $sqlpass, $dbname) or die ("DB-system no available");

    $query = "SELECT *
    FROM bigdata.xkcd_comics
    WHERE lower(safe_title) like '%". strtolower($_GET['search']) ."%'
    OR lower(alt) like '%". strtolower($_GET['search']) ."%'
    OR lower(title) like '%". strtolower($_GET['search']) ."%'
    ORDER BY num ASC;";
    $res = mysqli_query($my_db, $query);
    mysqli_close($my_db);
}

?>

<!DOCTYPE html>
<html lang="en">
<head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <link rel="stylesheet" href="styling.css">
</head>

<!-- As a heading -->
<nav class="navbar bg-dark navbar-dark p-3">
  <div class="container-fluid">
    <span class="navbar-brand mb-0 h1 href='#'">BigData-XKCD</span>
  </div>
</nav>

<body>
    <main class="m-2">

        <div class="d-flex justify-content-center mt-5">
            <div >
                <form class="form-inline" method="GET" action="/index.php">
                    <div class="row">
                        <div  class="col col-lg-8">
                            <input type="text" name="search" id="search" class="form-control" placeholder="Search">
                        </div>
                        <div  class="col col-lg-4">
                            <button type="submit" class="btn btn-primary mb-2">Search</button>
                        </div>
                    </div>
                </form>
            </div>
        </div>

        <section>
            <div class="container-result mt-5">
                <?php
                    if(isset($res)){
                        echo "<table class='table' border=0>";
                        echo "<tr>";
                        echo "<th class='fs-4' colspan='2'>Results:</th>";
                        echo "<th class='fs-4'>Title</th>";
                        echo "<th class='fs-4'>Link</th>";
                        echo "</tr>";
                        while($row = mysqli_fetch_assoc($res)){
                            echo "
                            <tr>
                                <td colspan='2'>
                                    <img src='". $row['img'] ."'/>
                                </td>
                                <td class='align-middle fs-5'>
                                    ". $row['title'] ."
                                </td>
                                <td class='align-middle fs-5'>
                                    <a href='https://xkcd.com/". $row['num'] ."/'> https://xkcd.com/". $row['num'] ."/ </a>
                                </td>
                            </tr>";
                        }
                        echo "</table>";
                    }
                ?>
            </div>
        </section>
    </main>
</body>
</html>