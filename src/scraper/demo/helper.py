# ruff: noqa
# ruff: noqa: PGH004
html_samples = {
    "all-cocktails": """
        <!-- https://www.example.com/all-cocktails -->
        <html><body>
        <div class="cocktails">
        <ul>
          <li class="cocktail"><a href="https://www.example.com/manhattan">Manhattan</a></li>
          <li class="cocktail"><a href="https://www.example.com/margarita">Margarita</a></li>
          <li class="cocktail"><a href="https://www.example.com/negroni">Negroni</a></li>
        </ul>
        </div>
        <div class="nav">
          <a class="next" href="https://www.example.com/all-cocktails/page/2">Next</a>
        </div>
        </body></html>
    """,
    "all-cocktails-pg2": """
        <!-- https://www.example.com/all-cocktails/page/2 -->
        <html><body>
        <div class="cocktails">
        <ul>
          <li class="cocktail"><a href="https://www.example.com/old-fashioned">Old Fashioned</a></li>
        </ul>
        </div>
        <div class="nav">
          <a class="next" href="https://www.example.com/all-cocktails/page/3">Next</a>
        </div>
        </body></html>
    """,
    "all-cocktails-pg3": """
        <!-- https://www.example.com/all-cocktails/page/3 -->
        <html><body>
        <div class="cocktails">
        <ul>
          <li class="cocktail"><a href="https://www.example.com/paper-plane">Paper Plane</a></li>
        </ul>
        </div>
        <div class="nav">
        </div>
        </body></html>
    """,
    "manhattan": """
        <!-- https://www.example.com/manhattan -->
        <html><body>
        <div class="cocktail">
        <h2>Manhattan</h2>
        <ul class="ingredients">
          <li>1 1/2 oz. Bourbon</li>
          <li>3/4 oz Sweet Vermouth</li>
          <li>2 dashes Angostura Bitters</li>
        </ul>
        <ul class="instructions">
          <li>Pour all ingredients into mixing glass with ice cubes.</li>
          <li>Stir well.</li>
          <li>Strain into a chilled cocktail glass.</li>
        </ul>
        <p class="garnish">Granish with cocktail cherry.</p>
        </div>
        </body></html>
    """,
    "margarita": """
        <!-- https://www.example.com/margarita -->
        <html><body>
        <div class="cocktail">
        <h2>Margarita</h2>
        <ul class="ingredients">
          <li>50 ml Tequila 100% Agave</li>
          <li>20 ml Triple Sec</li>
          <li>15 ml Freshly Squeezed lime Juice</li>
        </ul>
        <ul class="instructions">
          <li>Add all ingredients into a shaker with ice.</li>
          <li>Shake and strain into a chilled cocktail glass.</li>
        </ul>
        <p class="garnish">Half salt rim (Optional).</p>
        </div>
        </body></html>
    """,
    "negroni": """
        <!-- https://www.example.com/negroni -->
        <html><body>
        <div class="cocktail">
        <h2>Negroni</h2>
        <ul class="ingredients">
          <li>1 oz Gin</li>
          <li>1 oz Campari</li>
          <li>1 oz Sweet Vermouth</li>
        </ul>
        <ul class="instructions">
          <li>Pour all ingredients directly into chilled old fashioned glass filled with ice.</li>
          <li>Stir gently.</li>
        </ul>
        <p class="garnish">Granish with half orange slice.</p>
        </div>
        </body></html>
    """,
    "old-fashioned": """
        <!-- https://www.example.com/old-fashioned -->
        <html><body>
        <div class="cocktail">
        <h2>Old Fashioned</h2>
        <ul class="ingredients">
          <li>2 oz Bourbon or Rye</li>
          <li>1 Sugar Cube </li>
          <li>Few Dashes Angostura Bitters</li>
          <li>Few Dashes Plain Water</li>
        </ul>
        <ul class="instructions">
          <li>Place sugar cube in old fashioned glass and saturate with bitter, add few dashes of plain water. Muddle until dissolved. Fill the glass with ice cubes and add whiskey.</li>
          <li>Stir gently.</li>
        </ul>
        <p class="garnish">Granish with orange slice or zest, and a cocktail cherry.</p>
        </div>
        </body></html>
    """,
    "paper-plane": """
        <!-- https://www.example.com/paper-plane -->
        <html><body>
        <div class="cocktail">
        <h2>Paper Plane</h2>
        <ul class="ingredients">
          <li>1 oz Bourbon</li>
          <li>1 oz Amaro Nonino</li>
          <li>1 oz Aperol</li>
          <li>1 oz Lemon Juice</li>
        </ul>
        <ul class="instructions">
          <li>Pour all ingredients into cocktail shaker, shake well with ice.</li>
          <li>Strain into chilled cocktail glass..</li>
        </ul>
        <p class="garnish">N/A</p>
        </div>
        </body></html>
    """,
}
