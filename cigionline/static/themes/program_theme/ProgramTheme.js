import React, { useState } from 'react';
import PropTypes from 'prop-types';
import ProgramThemeRow from './ProgramThemeRow';

const ProgramTheme = (props) => {
  const themes = [
    {
      title: 'Data, Economy and Society',
      backgroundColour: 'lightest-grey',
      fontColour: 'black',
    },
    {
      title: 'AI and Transformative Technology',
      backgroundColour: 'light-grey',
      fontColour: 'black',
    },
    {
      title: 'Digitalization, Security and Democracy',
      backgroundColour: 'grey',
      fontColour: 'white',
    },
    {
      title: 'Global Cooperation and Governance',
      backgroundColour: 'dark-grey',
      fontColour: 'white',
    },
  ];
  const rows = [
    {
      title: 'Governance of Digital Money',
      backgroundColour: 'lightest-grey',
      fontColour: 'black',
      primaryTheme: 'Data, Economy and Society',
      secondaryTheme: ['Global Cooperation and Governance'],
    },
    {
      title: 'Digitalization of Trade',
      backgroundColour: 'lightest-grey',
      fontColour: 'black',
      primaryTheme: 'Data, Economy and Society',
      secondaryTheme: ['Global Cooperation and Governance'],
    },
    {
      title: 'Digital Platform Governance',
      backgroundColour: 'lightest-grey',
      fontColour: 'black',
      primaryTheme: 'Data, Economy and Society',
      secondaryTheme: ['Global Cooperation and Governance'],
    },
    {
      title: "Africa's Digital Transformation",
      backgroundColour: 'lightest-grey',
      fontColour: 'black',
      primaryTheme: 'Data, Economy and Society',
      secondaryTheme: [
        'Global Cooperation and Governance',
        'AI and Transformative Technology',
        'Digitalization, Security and Democracy',
      ],
    },
    {
      title: 'Governance of AI',
      backgroundColour: 'light-grey',
      fontColour: 'black',
      primaryTheme: 'AI and Transformative Technology',
      secondaryTheme: [],
    },
    {
      title: 'Advancing Responsible AI Governance in Military Operations',
      backgroundColour: 'light-grey',
      fontColour: 'black',
      primaryTheme: 'AI and Transformative Technology',
      secondaryTheme: ['Digitalization, Security and Democracy'],
    },
    {
      title: 'Data Valuation',
      backgroundColour: 'light-grey',
      fontColour: 'black',
      primaryTheme: 'AI and Transformative Technology',
      secondaryTheme: ['Data, Economy and Society'],
    },
    {
      title: 'Freedom of Thought',
      backgroundColour: 'grey',
      fontColour: 'white',
      primaryTheme: 'Digitalization, Security and Democracy',
      secondaryTheme: [],
    },
    {
      title: 'Space Governance 4.0',
      backgroundColour: 'grey',
      fontColour: 'white',
      primaryTheme: 'Digitalization, Security and Democracy',
      secondaryTheme: [
        'Data, Economy and Society',
        'Global Cooperation and Governance',
      ],
    },
    {
      title: 'Supporting Safer Digital Spaces',
      backgroundColour: 'grey',
      fontColour: 'white',
      primaryTheme: 'Digitalization, Security and Democracy',
      secondaryTheme: ['Data, Economy and Society'],
    },
    {
      title: 'Waterloo Security Dialogue',
      backgroundColour: 'grey',
      fontColour: 'white',
      primaryTheme: 'Digitalization, Security and Democracy',
      secondaryTheme: [],
    },
    {
      title: 'India and China in a Multipolar World',
      backgroundColour: 'dark-grey',
      fontColour: 'white',
      primaryTheme: 'Global Cooperation and Governance',
      secondaryTheme: [],
    },
    {
      title: 'Reform of Existing Multilateral Institutions',
      backgroundColour: 'dark-grey',
      fontColour: 'white',
      primaryTheme: 'Global Cooperation and Governance',
      secondaryTheme: ['Data, Economy and Society'],
    },
    {
      title: 'New Institutions for Digital Governance',
      backgroundColour: 'dark-grey',
      fontColour: 'white',
      primaryTheme: 'Global Cooperation and Governance',
      secondaryTheme: ['Data, Economy and Society'],
    },
    {
      title: 'Global Scenarios',
      backgroundColour: 'dark-grey',
      fontColour: 'white',
      primaryTheme: 'Global Cooperation and Governance',
      secondaryTheme: [],
    },
  ];

  const [activeProgram, setActiveProgram] = useState(null);

  const handleMouseEnter = (program) => {
    setActiveProgram(program);
    console.log(program)
  };

  const handleMouseLeave = () => {
    setActiveProgram(null);
  };

  return (
    <div className="program-theme">
      <div className="row themes-row">
        <div className="col-3" />
        <div className="col-1" />
        {themes.map((theme) => (
          <div className="col-2 px-1" key={theme.title}>
            <div className={`theme-title-wrapper bg-${theme.backgroundColour}`}>
              <h3
                className={`cell cell-title theme-cell theme-title bg-${theme.backgroundColour} fc-${theme.fontColour}`}
              >
                {theme.title}
              </h3>
            </div>
          </div>
        ))}
      </div>
      {rows.map((row, index) => (
        <ProgramThemeRow
          row={row}
          key={row.title}
          rowIndex={index}
          handleMouseEnter={handleMouseEnter}
          handleMouseLeave={handleMouseLeave}
          activeProgram={activeProgram}
        />
      ))}
    </div>
  );
};

ProgramTheme.propTypes = {};

export default ProgramTheme;
