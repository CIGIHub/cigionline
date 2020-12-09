import React from 'react';

import '../../css/components/SearchTableSkeleton.scss';

function randomString(minLen, maxLen) {
  const char = 'ABCDEFGH IJKLMNOP QRSTUVWX YZabcdef ghijklmn opqrstuv wxyz0123 456789';
  const strLength = minLen + Math.random() * (maxLen - minLen);
  let str = '';
  for (let i = 0; i < strLength; i += 1) {
    str += char[Math.floor(Math.random() * char.length)];
  }
  return str;
}

function SearchTableSkeleton() {
  return (
    <table className="search-table-skeleton custom-theme-table">
      <thead>
        <tr>
          <th colSpan="6" className="skeleton-blur skeleton-meta">Title</th>
          <th colSpan="3" className="skeleton-blur skeleton-meta">Expert</th>
          <th colSpan="2" className="skeleton-blur skeleton-meta">Topic</th>
          <th colSpan="2" className="skeleton-blur skeleton-meta">Type</th>
        </tr>
      </thead>
      <tbody>
        {Array(10).fill().map(() => (
          <tr>
            <td colSpan="6">
              <div className="table-infos-wrapper">
                <div className="table-infos">
                  <div className="table-title-link skeleton-blur skeleton-title">
                    {randomString(20, 50)}
                  </div>
                  <div className="table-infos-date skeleton-blur skeleton-meta">
                    {randomString(12, 15)}
                  </div>
                </div>
              </div>
            </td>
            <td colSpan="3">
              <div className="table-content">
                <ul className="custom-text-list">
                  <li>
                    <div className="table-content-link table-content-link-black skeleton-blur skeleton-meta">
                      {randomString(15, 20)}
                    </div>
                  </li>
                </ul>
              </div>
            </td>
            <td colSpan="2">
              <div className="table-content">
                <ul className="custom-text-list">
                  <li>
                    <div className="table-content-link search-table-skeleton-topic skeleton-blur skeleton-topic">
                      {randomString(10, 15)}
                    </div>
                  </li>
                </ul>
              </div>
            </td>
            <td colSpan="2">
              <div className="table-content">
                <ul className="custom-text-list">
                  <li>
                    <div className="table-content-link skeleton-blur skeleton-meta">
                      {randomString(5, 10)}
                    </div>
                  </li>
                </ul>
              </div>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default SearchTableSkeleton;
