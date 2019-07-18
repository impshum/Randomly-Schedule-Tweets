<?php
function gallery()
{
    $data = json_decode(file_get_contents('db.json'));
    $db = $data->_default;
    foreach ($db as $key) {
        $title = $key->title;
        $image = $key->image;
        $tweeted = $key->tweeted;
        if ($tweeted) {
            echo "
              <div class='column is-4'>
                  <figure class='image is-square'>
                    <img src='img/$image' alt='$title'>
                  </figure>
              </div>
            ";
        }
    }
}
?>

<!DOCTYPE html>
<html>

<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Image Thing</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bulma/0.7.5/css/bulma.min.css">
  <style>
    .is-square img {
      width: 100%;
      object-fit: cover;
    }
  </style>
</head>

<body>

  <section class="section is-medium">
    <div class="container has-text-centered">
      <div class="columns is-multiline">
        <?php gallery(); ?>
      </div>
    </div>
  </section>

</body>

</html>
