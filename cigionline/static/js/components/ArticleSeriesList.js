import React, { useEffect, useState } from 'react';
import ArticleSeriesListing from './ArticleSeriesListing';
import Paginator from './Paginator';

const ArticleSeriesList = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const [pages, setPages] = useState([]);
  const [pageCount, setPageCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [rows, setRows] = useState([]);

  const getRows = () => {
    const uri = '/api/article-series/';

    fetch(encodeURI(uri))
      .then((res) => res.json())
      .then((data) => {
        const allRows = data.items;

        // loop through rows and create an array of pages with 6 rows each
        const allPages = [];
        let page = [];
        allRows.forEach((row) => {
          if (page.length === 6) {
            allPages.push(page);
            page = [];
          }
          page.push(row);
        });
        allPages.push(page);

        setPages(allPages);
        setPageCount(allPages.length);
        setRows(allPages[0]);
        setLoading(false);
        setCurrentPage(1);
      });
  };

  const setPage = (page) => {
    setRows(pages[page - 1]);
    setCurrentPage(page);
  };

  useEffect(() => {
    getRows();
  }, []);

  return (
    <div className="container">
      <div className="row g-3">
        {loading
          ? <div>Loading...</div>
          : rows.map((row) => (
            <>
              <div className="col-12">
                <ArticleSeriesListing
                  key={row.id}
                  row={row}
                />
              </div>
              {row !== rows[rows.length - 1] && (
                <div className="col-12">
                  <hr />
                </div> 
              )}
            </>
          ))}
      </div>
      <Paginator
        currentPage={currentPage}
        setPage={(page) => setPage(page)}
        totalPages={pageCount}
      />
    </div>
  );
};

export default ArticleSeriesList;